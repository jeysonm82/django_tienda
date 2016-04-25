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
    def __init__(self, product_pk, quantity, name, price, category_pk, image, discount):
        self.product_pk = product_pk
        self.quantity = quantity
        self.name = name
        self.price = price
        self.category_pk = category_pk
        self.discount = discount

        if image is not None:
            self.image = image.image.thumbnail['200x150'].url
        else:
            self.image = None

class CartEntrySerializer(serializers.Serializer):
    product_pk = serializers.CharField() 
    quantity = serializers.IntegerField()
    name = serializers.CharField(read_only=True) 
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    category_pk = serializers.IntegerField(read_only=True) 
    image = serializers.CharField(read_only=True) 
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    cart = None
    request = None

    def create(self, validated_data):
        try:
            prod = Product.objects.get(pk=validated_data.get('product_pk'))
            qty = validated_data.get('quantity')
        except Exception as e:
            print "error", e
        else:
            self.cart.add(prod, qty)
            return CartEntry(prod.pk, self.cart.storage[prod], prod.name,
                    prod.price, prod.get_first_category().pk,
                    prod.images.first(), prod.calculate_discount(self.request.discounts))
        
    def update(self, instance, validated_data):
        qty = self.validated_data.get('quantity')
        self.cart.update(Product.objects.get(pk=instance.product_pk), qty)
        instance.quantity = qty
        return instance


class CartRESTView(APIView):

    def _get_entire_cart(self, request, cart):     
        entries = []
        for p, q in cart.storage.iteritems():
            entries.append(CartEntry(p.pk, q, p.name, p.price,
                p.get_first_category().pk, p.images.first(),
                 p.calculate_discount(request.discounts)))

        serializer = CartEntrySerializer(entries, many=True)

        return serializer
    

class CartEntryDetailRESTView(CartRESTView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request, pk, format=None):
        cart = Cart(request.cart)
        CartEntrySerializer.cart = cart

        product = Product.objects.get(pk=pk)
        entry  = CartEntry(pk, cart.storage[product], product.name,
                product.price, product.get_first_category().pk,
                product.images.first(), product.calculate_discount(request.discounts))
        serializer = CartEntrySerializer(entry)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        cart = Cart(request.cart)
        CartEntrySerializer.cart = cart
 
        product = Product.objects.get(pk=pk)
        cart.remove(product)

        #return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(self._get_entire_cart(request, cart).data)


    def put(self, request, pk, format=None):
        cart = Cart(request.cart)
        CartEntrySerializer.cart = cart

        product = Product.objects.get(pk=pk)
        entry  = CartEntry(pk, cart.storage[product], product.name,
                   product.price, product.get_first_category().pk,
                   product.images.first(), product.calculate_discount(request.discounts))
        serializer = CartEntrySerializer(entry, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(self._get_entire_cart(request, cart).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CartEntryListRESTView(CartRESTView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        cart = Cart(request.cart)
        CartEntrySerializer.cart = cart
        return Response(self._get_entire_cart(request, cart).data)



    def post(self, request, format=None):
        cart = Cart(request.cart)
        CartEntrySerializer.cart = cart
        CartEntrySerializer.request = request

        serializer = CartEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(self._get_entire_cart(request, cart).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
