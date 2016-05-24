# -*- coding: utf-8 -*-
from django.views.generic import TemplateView, FormView, View, RedirectView
from django.core.urlresolvers import reverse_lazy
from tienda.cart import Cart
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tienda.views.cart import CartEntrySerializer, CartEntry
from rest_framework import permissions
from tienda.shipping import ShippingMethodRegister
from tienda.payment import PaymentMethodRegister
from tienda.models import Order
from tienda.models import Address


SESSION_KEY = 'TIENDA_CHECKOUT_KEY'

class Checkout(object):
    request = None
    user = None

    def __init__(self, checkout_storage):
        self.checkout_storage = checkout_storage

    def start(self, cart):
        checkout_storage = self.checkout_storage
        checkout_storage[u'cart'] = cart.session_storage #TODO shallow copy?
        checkout_storage[u'address'] = None
        checkout_storage[u'city'] = None
        checkout_storage[u'shipping_method'] = None
        checkout_storage[u'shipping_price'] = None
        checkout_storage[u'payment_method'] = None
        self.checkout_storage[u'shipping_method_data'] = {}

    @property
    def cart(self):
        return Cart(self.checkout_storage[u'cart'])

    @property
    def cart_entries(self):
        entries = []
        for p, q in self.cart.storage.iteritems():
            entries.append(CartEntry(p.pk, q, p.name, p.price,
                p.get_first_category().pk, p.images.first(),
                 p.calculate_discount(Checkout.request.discounts)))
        return entries
    
    @property
    def shipping_address(self):
        return self.checkout_storage[u'address']

    @shipping_address.setter
    def shipping_address(self, address):
        self.checkout_storage[u'address'] = address

    @property
    def shipping_address_city(self):
        return self.checkout_storage[u'city']

    @shipping_address_city.setter
    def shipping_address_city(self, address):
        self.checkout_storage[u'city'] = address


    @property
    def shipping_method(self):
        return self.checkout_storage[u'shipping_method']

    @shipping_method.setter
    def shipping_method(self, shipping):
        self.checkout_storage[u'shipping_method'] = shipping
        shipm = ShippingMethodRegister.get(shipping)()
        if self.request:
            shipm.data = self.request.data
            self.checkout_storage[u'shipping_method_data'] = shipm.data
        price = shipm.calculate()
        self.shipping_price = price       

    @property
    def shipping_price(self):
        return self.checkout_storage[u'shipping_price']

    @shipping_price.setter
    def shipping_price(self, price):
        self.checkout_storage[u'shipping_price'] = price

    @property
    def payment_method(self):
        return self.checkout_storage[u'payment_method']

    @payment_method.setter
    def payment_method(self, payment):
        self.checkout_storage[u'payment_method'] = payment

    def create_order(self):
        # preconditions
        if self.user is None:
            raise CreateOrderException("No hay usuario en el sistema")
        if self.payment_method is None:
            raise CreateOrderException(u"Método de pago no válido")
        if self.shipping_method is None:
            raise CreateOrderException(u"Método de envío pago no válido")
        if self.shipping_address is None or self.shipping_address_city is None:
            raise CreateOrderException(u"Dirección de envío no válida")
        cart_entries = self.cart.storage
        if(not len(cart_entries)):
            raise CreateOrderException(u"No hay productos en el carrito")
        # Instantiation and order creation
        #user = self.request.user.storeuser
        shipm = ShippingMethodRegister.get(self.shipping_method)()
        shipm.data = self.checkout_storage[u'shipping_method_data']
        paym = PaymentMethodRegister.get(self.payment_method)()

        default_address = self.user.default_address()
        shipping_address = Address()
        shipping_address.street_address_1 = self.shipping_address
        shipping_address.city = self.shipping_address_city
        shipping_address.phone = default_address.phone
        shipping_address.mobile = default_address.mobile
        shipping_address.first_name = default_address.first_name
        shipping_address.last_name = default_address.last_name
        shipping_address.title = "-"
        shipping_address.city_area = "-"
        shipping_address.save()

        
        discounts = self.request.discounts if self.request else None

        order = Order.objects.create_order(self.user, shipping_address, shipm, paym, cart_entries, discounts)
        print "Order created: ", order
        return order

class CreateOrderException(Exception):
    pass

class CheckoutSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(allow_null=True)
    shipping_address_city = serializers.CharField(allow_null=True)
    shipping_method = serializers.CharField(allow_null=True)
    shipping_price = serializers.IntegerField(read_only=True)
    payment_method = serializers.CharField(allow_null=True)
    cart_entries = CartEntrySerializer(many=True, read_only=True)

    def create(self, validated_data):
        return None

    def update(self, instance, validated_data):
        #instance.shipping_price = # TODO
        if 'payment_method' in self.validated_data:
            instance.payment_method = self.validated_data.get('payment_method')

        if 'shipping_address' in self.validated_data:
            instance.shipping_address = self.validated_data.get('shipping_address')
        if 'shipping_address_city' in self.validated_data:
            instance.shipping_address_city = self.validated_data.get('shipping_address_city')

        if 'shipping_method' in self.validated_data:
            instance.shipping_method = self.validated_data.get('shipping_method')
        return instance


class CheckoutDetailRESTView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        Checkout.request = request
        if SESSION_KEY not in self.request.session:
            self.request.session[SESSION_KEY] = {}

        checkout = Checkout(self.request.session[SESSION_KEY])
        serializer = CheckoutSerializer(checkout)
        return Response(serializer.data)

    def put(self, request):
        Checkout.request = request
        if SESSION_KEY not in self.request.session:
            self.request.session[SESSION_KEY] = {}
        checkout = Checkout(self.request.session[SESSION_KEY])
        # TODO shipping_price
        serializer = CheckoutSerializer(checkout, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""
1.InitCheckoutView initializes the checkout object with a cart object
and redirects to CheckoutView.

2.CheckoutView creates the frontend with the steps to complete checkout process.
This frontend should show the checkout attributes like shipping_address, address, payment_method, and should provide controls to allow the user to update those attrs.

3. CheckoutDetailRESTView is a REST API  to GET and update (PUT) the checkout obj attributes (shipping, address, etc.) via async requests (Ajax).
This is used by the frontend created by CheckoutView.

4. Finally CreateOrderView is called by the frontend when the checkout process is finalized and the order needs to be generated. 

5. Once it's generated the user is redirected to the OrderDetailView.
"""

class InitCheckoutView(RedirectView):
    checkout = None

    def get_redirect_url(self, *args, **kwargs):
        #TODO redirect t o login/register and dont start chechout
        cart = Cart(self.request.cart)
        if SESSION_KEY not in self.request.session:
            self.request.session[SESSION_KEY] = {}
        self.checkout = Checkout(self.request.session[SESSION_KEY])
        self.checkout.start(cart)

        url = reverse_lazy('checkout')
        return url

class CheckoutView(TemplateView):
    template_name = ''
