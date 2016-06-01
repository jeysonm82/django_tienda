from django.views.generic import TemplateView, ListView
from django.http import HttpResponse
from tienda.models import Category, Product, ProductManager
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import generics


class CatalogView(ListView):
    template_name = 'more/catalog/catalog.html'
    queryset = Product.objects.none()
    context_object_name = 'products_list'
    paginate_by = settings.PRODUCTS_PER_PAGE

    def get_queryset(self):
        self.category = None
        if 'cat_id' in self.kwargs:
            self.category = get_object_or_404(Category, pk=self.kwargs['cat_id'])
        # Queryset overriding
        if self.category is None:

            if 'search' in self.request.GET:
                # If 's' in GET then use search manager
                content = self.request.GET.get('search')
                queryset = Product.search.filter(content=content, enabled=True)
            else:
                queryset = Product.objects.filter(enabled=True) # TODO que productoss obtener por defecto?
        else:
            queryset = Product.objects.get_products_from_cat(self.category)

        if 'discounts_only' in self.request.GET:
            dqset = Product.objects.none() 
            for discount in self.request.discounts:
                qset = discount.get_products_queryset()
                dqset |= qset
            # Method 1 id IN (Subquery)
            discounted_products = dqset.distinct().values_list('pk', flat=True)
            queryset = queryset.filter(pk__in=discounted_products)


        ordering = self.get_ordering()
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset
    
    def get_context_data(self, **kwargs):
        """ Show all products if no category, else, filter by cat """
        context = super(CatalogView, self).get_context_data( **kwargs)
        category_list = Category.objects.all()
        context['category'] = self.category
        context['category_list'] = category_list
        return context


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name')

class AdminProductListRESTView(generics.ListAPIView):
    """Used for catalogdiscount admin to filter list of products"""
    queryset = Product.objects.all_noprefetch()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self):
        qset = super(AdminProductListRESTView, self).get_queryset()
        if "name" in self.request.GET:
            qset = qset.filter(name__contains=self.request.GET.get("name"))
        return qset
