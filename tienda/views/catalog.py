from django.views.generic import TemplateView, ListView
from django.http import HttpResponse
from tienda.models import Category, Product, ProductManager, ProductImage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import generics
from django.db.models import Q

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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'slug', 'name')

class CatalogProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('_image', read_only=True)
    categories = CategorySerializer(many=True)

    def _image(self, obj):
        try:
            return obj.images.first().image.crop['350x350'].url
        except:
            return ''

    class Meta:
        model = Product
        fields = ('id','name', 'uid', 'image', 'get_slug', 'categories')


class CatalogRESTView(generics.ListAPIView):
    serializer_class = CatalogProductSerializer
    queryset = Product.objects.all_noprefetch()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super(CatalogRESTView, self).get_queryset()
        if 'pk' in self.kwargs:
            cat = Category.objects.get(pk=self.kwargs['pk'])
            queryset = Product.objects.get_products_from_cat(cat)
        return queryset
 

class AdminProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name','uid')

class AdminProductListRESTView(generics.ListAPIView):
    """Used for catalogdiscount admin to filter list of products"""
    queryset = Product.objects.all_noprefetch()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AdminProductSerializer

    def get_queryset(self):
        qset = super(AdminProductListRESTView, self).get_queryset()
        if "name" in self.request.GET:
            q_queries = None
            for i, s in enumerate(self.request.GET.get('name').split(',')):
                s = s.strip()
                if not len(s):
                    continue
                if q_queries is None:
                    q_queries = Q(name__contains=s) | Q(uid__contains=s)
                else:
                    q_queries = q_queries | Q(name__contains=s) | Q(uid__contains=s)
            qset = qset.filter(q_queries)[:250]

        return qset
