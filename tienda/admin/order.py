from django.contrib import admin
from tienda.models import Order, ProductOrder,Address, Payment


class ProductOrderInline(admin.TabularInline):
    model = ProductOrder

class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    model = Order
    inlines = [ProductOrderInline, PaymentInline]
    readonly_fields = ['total', 'user', 'full_address', 'shipping_method', 'extra']
    search_fields = ['token']


