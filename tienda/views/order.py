from django.views.generic import TemplateView, FormView, View, RedirectView, DetailView
from tienda.views.checkout import Checkout, SESSION_KEY
from django.core.urlresolvers import reverse_lazy
from tienda.models import Order, ProductOrder
from tienda.cart import Cart
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import generics

TOKEN_PATTERN = ('(?P<token>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}'
                 '-[0-9a-z]{12})')

class CreateOrderView(RedirectView):
    checkout = None

    def create_order(self):
        order = self.checkout.create_order()
        return order

    def get_redirect_url(self, *args, **kwargs):
        Checkout.request = self.request
        try:
            self.checkout = Checkout(self.request.session[SESSION_KEY])
            self.checkout.user = self.request.user.storeuser
            order = self.create_order()
            del self.request.session[SESSION_KEY]

            # Empty cart
            cart = Cart(self.request.cart)
            cart.remove_all() #TODO remove the products in order only
            del self.request.session['TIENDA_CART_KEY'] #TODO get key from settings
            self.request.cart = {}

        except Exception as e:
            url = reverse_lazy('checkout')
            print "ERROR", e
        else:
            url = reverse_lazy('view-order', kwargs={'token': order.token})
        return url


class OrderDetailView(DetailView):
    model = Order


    def get_object(self):
        return Order.objects.get(token=self.kwargs['token'])

class ProductOrderSerializer(serializers.ModelSerializer):
    discount = serializers.SerializerMethodField("_discount") #renaming discount_price to discount
    image = serializers.SerializerMethodField("_product_image")
    name = serializers.SerializerMethodField("_product_name")
    product_pk = serializers.SerializerMethodField("_product_pk")

    def _discount(self, obj):
        return float(obj.discount_price)

    def _product_image(self, obj):
        img = obj.product.images.first()
        if img is not None:
            return img.image.thumbnail['200x150'].url

    def _product_name(self, obj):
        return obj.product_name

    def _product_pk(self, obj):
        return obj.product.pk

    class Meta:
        model = ProductOrder
        fields = ('id', 'product_pk', 'name', 'quantity', 'price', 'discount', 'tax', 'discount_price', 'image')

class OrderSerializer(serializers.ModelSerializer):
    products = ProductOrderSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "token", "products", "shipping_price")

class OrderDetailRESTView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
