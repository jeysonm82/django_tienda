# -*- coding: utf-8 -*-
from django.contrib import admin
from tienda.models import ProductImage, Product, Category
from mptt.forms import TreeNodeChoiceField, TreeNodeMultipleChoiceField
from django import forms

class ProductImagesInline(admin.TabularInline):
    """ Inline for Product's images """
    model = ProductImage
    extra = 1
    max_num = 1
    verbose_name = "Imágenes de producto"

class ProductForm(forms.ModelForm):

    """ Form for Product """
    categories = TreeNodeMultipleChoiceField(queryset=Category.objects.all(), label= 'Categoria')

    class Meta:
        model = Product
        exclude=('available_on',)

class ProductAdmin(admin.ModelAdmin):
    """ Product  admin. It has an inline for productvariants """
    list_display = ('name','category','price')
    form = ProductForm
    fieldsets = (
        (None, {
            'fields': ('name', 'uid', 'description','price'),
        }),
        ("Categoria" +'', {'fields': ('categories',)}),

    )
    inlines = [ProductImagesInline]

    
    def category(self, obj):
        return obj.get_first_category()
    category.short_description = Category._meta.verbose_name
    category.admin_order_field = 'categories__name'
