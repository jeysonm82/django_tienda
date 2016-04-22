from django.contrib import admin
from catalog import CategoryAdmin,CatalogDiscountAdmin
from product import ProductAdmin
from tienda.models import Category, Product, CatalogDiscount

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(CatalogDiscount, CatalogDiscountAdmin)
