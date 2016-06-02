from django.contrib import admin
from tienda.models import Order, ProductOrder,Address, Payment


class ProductOrderInline(admin.TabularInline):
    model = ProductOrder
    fields = ['product_name','product_uid', 'quantity', 'price', 'discount_price', 'tax']

class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    model = Order
    inlines = [ProductOrderInline, PaymentInline]
    search_fields = ['token']
    list_display = ('ref','created','num_products', 'status', 'shipping_address', 'extra')
    readonly_fields = ['discounts', 'extra', 'user']
    exclude=['shipping_method','total']

    def num_products(self, obj):
        if obj is not None:
            return "%s"%(obj.products.count())
    num_products.short_description = u"# productos"
