from django.contrib import admin
from catalog import CategoryAdmin,CatalogDiscountAdmin
from product import ProductAdmin
from order import OrderAdmin
from tienda.models import Category, Product, CatalogDiscount, Order
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(CatalogDiscount, CatalogDiscountAdmin)
admin.site.register(Order, OrderAdmin)
