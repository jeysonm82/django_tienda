from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.http import HttpResponse
from tienda.models import Product, Category
from tienda.cart import Cart
from django import forms
import json
from django.contrib import messages



class ProductDetail(DetailView):

    """Product detail view"""

    template_ = "more/product_detail.html"
    model = Product
    context_object_name = 'product'
    obj = None
    form = None

    def get_form(self):
        return None

    def get_object(self, queryset=None):
        """ Returns product instance. The instance is cached to reduce queries """
        if self.obj is None:
            self.obj = super(ProductDetail, self).get_object(queryset)
        return self.obj

    def get_queryset(self):
        p = super(ProductDetail, self).get_queryset().prefetch_related(
            'images')
        return p

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        product = self.get_object()
        context['category'] = product.get_first_category()
        context['category_list'] = Category.objects.all()
        context['form'] = self.get_form()
        return context
