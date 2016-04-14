from django.contrib import admin
from catalog import CategoryAdmin
from product import ProductAdmin
from tienda.models import Category, Product

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
