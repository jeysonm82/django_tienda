from rest_framework import serializers
from tienda.models import Product
from rest_framework.views import APIView
from collections import namedtuple
from tienda.cart import Cart
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

CartEntry = namedtuple('CartEntry', ['product_pk', 'quantity'])


class CartEntrySerializer(serializers.Serializer):
    product_pk = serializers.CharField() 
    quantity = serializers.IntegerField()

    cart = None

    def create(self, validated_data):
        try:
            prod = Product.objects.get(pk=validated_data.get('product_pk'))
            qty = validated_data.get('quantity')
        except Exception as e:
            print "error", e
        else:
            self.cart.add(prod, qty)
            return CartEntry(prod.pk, self.cart.storage[prod])
        
    def update(self, instance, validated_data):
        try:
            prod = Product.objects.get(pk=self.validated_data.get('product_pk'))
            qty = self.validated_data.get('quantity')
        except Exception as e:
            print "error", e
        else:
            self.cart.update(prod, qty)
            return CartEntry(prod.pk, qty)


class CartEntryDetailRESTView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request, pk, format=None):
        cart = Cart(request.cart)
        CartEntrySerializer.cart = cart

        product = Product.objects.get(pk=pk)
        entry  = CartEntry(pk, cart.storage[product])
        serializer = CartEntrySerializer(entry)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        cart = Cart(request.cart)
        CartEntrySerializer.cart = cart
 
        product = Product.objects.get(pk=pk)
        cart.remove(product)

        return Response(status=status.HTTP_204_NO_CONTENT)

class CartEntryListRESTView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        cart = Cart(request.cart)
        CartEntrySerializer.cart = cart
        
        entries = []
        for p, q in cart.storage.iteritems():
            entries.append(CartEntry(p.pk, q))
        serializer = CartEntrySerializer(entries, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):
        cart = Cart(request.cart)
        CartEntrySerializer.cart = cart
        serializer = CartEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
