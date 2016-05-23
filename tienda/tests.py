from django.test import TestCase
from tienda.cart import Cart
from tienda.views.checkout import Checkout
from tienda.models import Product,Category, StoreUser,Address
from tienda.shipping import ShippingMethod, ShippingMethodRegister
from tienda.payment import PaymentMethod, PaymentMethodRegister

# Create your tests here.
class CheckoutTests(TestCase):

    def test_checkout(self):
        # Initial data setup
        user = StoreUser()
        user.username = "Test"
        user.first_name = "Juan"
        user.last_name = "Perez"
        user.gov_id = "123456"
        user.save()
        def_addr = Address()
        def_addr.title = "-"
        def_addr.street_address_1 = "Cll 123 456"
        def_addr.city = "City"
        def_addr.city_area= "-"
        def_addr.phone = "123"
        def_addr.mobile = "123"
        def_addr.first_name = user.first_name
        def_addr.last_name = user.last_name
        def_addr.save()
        user.addresses.add(def_addr)
        
        PROD_QTY = 2
        PROD_PRICE = 20000
        product = Product()
        product.uid = "001"
        product.name = "Test product"
        product.price = PROD_PRICE
        product.save()

        cart = Cart({})
        cart.add(product, PROD_QTY)

        # Actual test
        checkout = Checkout({})
        checkout.start(cart)
        checkout.user = user
        checkout.shipping_method = "shipping_test"
        checkout.payment_method = "payment_test"
        checkout.shipping_address = "Cll 123 45-6"
        checkout.shipping_address_city = "City"

        order = checkout.create_order()

        porder = order.products.first()
        self.assertEqual(order.total, product.price*PROD_QTY + 1000)
        self.assertEqual(len(order.products.all()), 1)
        self.assertEqual(porder.product, product)
        self.assertEqual(porder.quantity,PROD_QTY)
        self.assertEqual(porder.price, product.price)

class ShippingMethodTest(ShippingMethod):
    ref = "shipping_test"
    
    def calculate(self):
        return 1000

class PaymentMethodTest(PaymentMethod):
    ref = "payment_test"
    payment_ref = "00001"

ShippingMethodRegister.register(ShippingMethodTest)
PaymentMethodRegister.register(PaymentMethodTest)
