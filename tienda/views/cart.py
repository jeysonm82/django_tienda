from rest_framework import serializers
from tienda.models import Product
from rest_framework.views import APIView
from collections import namedtuple
from tienda.cart import Cart
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

#CartEntry = namedtuple('CartEntry', ['product_pk', 'quantity'])

class CartEntry(object):
    def __init__(self, product_pk, quantity, name, price):
        self.product_pk = product_pk
        self.quantity = quantity
        self.name = name
        self.price = price

class CartEntrySerializer(serializers.Serializer):
    product_pk = serializers.CharField() 
    quantity = serializers.IntegerField()
    name = serializers.CharField(read_only=True) 
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    cart = None

    def create(self, validated_data):
        try:
            prod = Product.objects.get(pk=validated_data.get('product_pk'))
            qty = validated_data.get('quantity')
        except Exception as e:
            print "error", e
        else:
            self.cart.add(prod, qty)
            return CartEntry(prod.pk, self.cart.storage[prod], prod.name, prod.price)
        
    def update(self, instance, validated_data):
        qty = self.validated_data.get('quantity')
        self.cart.update(Product.objects.get(pk=instance.product_pk), qty)
        instance.quantity = qty
        return instance


class CartEntryDetailRESTView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request, pk, format=None):
        cart = Cart(request.cart)
        CartEntrySerializer.cart = cart

        product = Product.objects.get(pk=pk)
        entry  = CartEntry(pk, cart.storage[product], product.name, product.price)
        serializer = CartEntrySerializer(entry)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        cart = Cart(request.cart)
        CartEntrySerializer.cart = cart
 
        product = Product.objects.get(pk=pk)
        cart.remove(product)

        return Response(status=status.HTTP_204_NO_CONTENT)


    def put(self, request, pk, format=None):
        cart = Cart(request.cart)
        CartEntrySerializer.cart = cart

        product = Product.objects.get(pk=pk)
        entry  = CartEntry(pk, cart.storage[product], product.name, product.price)
        serializer = CartEntrySerializer(entry, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CartEntryListRESTView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        cart = Cart(request.cart)
        CartEntrySerializer.cart = cart
        return Response(self._get_entire_cart(cart).data)

    def _get_entire_cart(self, cart):     
        entries = []
        for p, q in cart.storage.iteritems():
            entries.append(CartEntry(p.pk, q, p.name, p.price))
        serializer = CartEntrySerializer(entries, many=True)

        return serializer

    def post(self, request, format=None):
        cart = Cart(request.cart)
        CartEntrySerializer.cart = cart
        serializer = CartEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(self._get_entire_cart(cart).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
