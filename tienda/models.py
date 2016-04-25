# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible, smart_text
from mptt.models import MPTTModel
from mptt.managers import TreeManager
from django.db.models import Manager
from django.conf import settings
from django_prices.models import PriceField
from versatileimagefield.fields import VersatileImageField, PPOIField
from unidecode import unidecode
from django.utils.text import slugify
from haystack.query import SearchQuerySet
from django.db.models import Q

# Create your models here.
@python_2_unicode_compatible
class Category(MPTTModel):

    name = models.CharField('name', max_length=128)
    slug = models.SlugField('slug', max_length=50, null=True, blank=True)
    description = models.TextField('description', blank=True, default='')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children',verbose_name='parent')
    visible = models.BooleanField('visible', default=True)
    uid = models.CharField('Ref', max_length=32, unique=True, blank=True, null=True)
    objects = Manager()
    tree = TreeManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'


class ProductManager(models.Manager):

    """ Product manager for product for table level operations """

    def get_products_from_cat(self, category):
        """ Gets products from category and child categories """
        if category is None:
            # TODO.prefetch_related('images', 'images__thumbnail_set')
            return self.get_queryset()
        cats = [x.pk for x in [category] + list(category.get_descendants())]
        # TODO.prefetch_related('images')
        return self.get_queryset().filter(enabled=True, categories__pk__in=cats)

    def recommended(self, category=None, num=3):
        return self.get_products_from_cat(category).order_by('?')[:num]

    def featured(self, category=None):
        # .order_by('?')
        #return self.get_products_from_cat(category).filter(featured=True)
        pass


class ProductSearchManager(models.Manager):
    """ Product manager using django haystack queryset for search"""
    haystack_qset = SearchQuerySet().all()

    def get_queryset(self):
        return self.haystack_qset
    
    def all(self):
        return self._get_django_qset(self.get_queryset())

    def filter(self, **kwargs):
        return self._get_django_qset(self.get_queryset().filter(**kwargs))

    def _get_django_qset(self, hay_qset):
        pks = [x.object.pk for x in hay_qset]
        return Product.objects.filter(pk__in=pks)

class Product(models.Model):
    name = models.CharField('name', max_length=128)
    description = models.TextField('description', blank=True, default='')
    price = models.DecimalField('price', max_digits=12, decimal_places=2)
    uid = models.CharField('Ref', max_length=32, unique=True)
    categories = models.ManyToManyField(Category, related_name='products')
    attributes = models.ManyToManyField('ProductAttribute', related_name='products', blank=True)
    updated_at = models.DateTimeField('updated at', auto_now=True, null=True)
    enabled = models.BooleanField('enabled', default=True)
    discount = None
    discount_value = 0
    objects = ProductManager()
    search = ProductSearchManager()

    def __unicode__(self):
        return self.name

    def get_first_category(self):
        return self.categories.filter(visible=True).first()

    def __hash__(self):
        return hash((self.pk, self.name))

    def __eq__(self, other):
        if not isinstance(other, Product):
            return False
        
        return (self.pk, self.name) == (other.pk, other.name)

    def get_price(self):
        return self.price

    def get_slug(self):
        return slugify(smart_text(unidecode(self.name)))
    
    def price_with_discount(self):
        return self.price - self.discount_value

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'

class ProductVariant(models.Model):
    name = models.CharField('name', max_length=128)
    price = models.DecimalField('price', max_digits=12, decimal_places=2)
    product = models.ForeignKey(Product, related_name='variants')


class ProductAttribute(models.Model):
    pass


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images')
    image = VersatileImageField(
        upload_to='products', ppoi_field='ppoi', blank=False)

    ppoi = PPOIField()
    alt = models.CharField('short description', max_length=128, blank=True)

    class Meta:
        verbose_name = 'imagen de producto'
        verbose_name_plural = 'imagenes de producto'

class CategoryImage(models.Model):
    category = models.ForeignKey(Category, related_name='images')
    image = VersatileImageField(
        upload_to='categories', ppoi_field='ppoi', blank=False)
    ppoi = PPOIField()
    alt = models.CharField('short description', max_length=128, blank=True)


class RuleBasedDiscount(models.Model):

    """Clase base abstracta para crear modelos de descuento basados en reglas para aplicar el descuento.
    Los descuentos basados en reglas heredan de esta.

    - Se puede definir el descuento como valor fijo o porcentaje.
    - Se puede establecer que el descuento solo se aplique si el usuario ingresa un cupón
    - Se puede definir la fecha inicial y final donde el descuento es válido

    Las reglas que se definen pueden ser reglas para aplicar descuentos a productos del catalogo
    (ver CatalogDiscount y CatalogDiscountRule) o reglas que aplican descuentos a un carrito de compras.
    """

    name = models.CharField("Nombre", max_length=255)
    """Nombre"""
    description = models.TextField("Descripción")
    # products =  None #models.ManyToManyField(Product, blank=True)
    discount = models.IntegerField("Descuento")
    """Valor nominal del descuento"""
    discount_unit = models.SmallIntegerField(
        "Unidad de descuento", default=2, choices=((1, 'Valor fijo'), (2, 'Porcentaje')))
    """Unidad del descuento (valor fijo o porcentaje)"""

    activated_by_coupon = models.BooleanField(
        "Activado con cupón", default=False, blank=True)
    """El descuento solo se aplica si se activa ingresando el coupon en la vista del carrito"""
    coupon = models.CharField("Cupon", max_length=50, null=True, blank=True)
    """Codigo del cupón"""
    date_from = models.DateField("Fecha inicio")
    date_to = models.DateField("Fecha fin")
    """Fecha inicio y final donde aplica el descuento"""

    enabled = models.BooleanField("Habilitado", default=False)
    """Si esta habilitado o no el descuento"""

    priority = models.SmallIntegerField("Prioridad", default=0, blank=True)
    """Prioridad del descuento. Para cuando hay varios descuentos"""

    days = models.CommaSeparatedIntegerField("Días", default='1,2,3,4,5,6,7', max_length=20, blank=True)
    """Días en los que aplica el descuento"""
 
    # TODO A futuro lo siguiente:
    """
    user: Especificar un usuario el cual sera el unico que pueda aplicar el cupón si se define
    coupon_qty: Cantidad de cupónes disponibles
    """

    def __repr__(self):
        return 'RuleBasedProductDiscount(name=%r, discount=%r, percent=%s)' % (
            self.name, str(self.discount), 'Yes' if self.discount_unit == 2 else 'No')

    def __unicode__(self):
        return self.name


    class Meta:
        abstract = True

class NotApplicableException(Exception):
    pass

class CatalogDiscount(RuleBasedDiscount):

    """Descuentos de catalogo que aplican rebajas a los precios de los productos en el catalogo que 
    pasan las reglas de descuento (CatalogDiscountRule).
    Funciona de dos maneras:
    1. Si este descuento esta habilitado y no se activa mediante cupón entonces el descuento
    se aplica directamente en el catalogo y muestra los precios descontados en la vista producto.
    Ej: Descuento del 20% para todos las productos de la categoria X

    2. Si se especifica cupón entonces cuando  el usuario ingrese el cupón este descuento aplicara a los
    productos del carrito que pasen las reglas de este descuento. Es lo mismo que 1 pero solo se activa cuando 
    se ingresa el cupón.
    Ej: Descuento del 20% para todos los productos de la categoría X ingresando el cupón DESCUENTO
    """

    def check_product(self, product):
        """Chequea el producto  aplicandole todas las reglas de este descuento.
        Si supera las reglas se calcula el descuento y se devuelve.
        """
        b = False
        for i, rule in enumerate(list(self.rules.all())):
            b = b or rule.check_product(product) 

        if not b:
            raise NotApplicableException('El producto no ha superado las reglas para aplicar este descuento')
        # Obtener descuento
        price = product.price
        discount = price * self.discount / 100 if self.discount_unit == 2 else self.discount
        discount = discount.quantize(1) # para redondear el obj Price

        if discount > price:
            raise NotApplicableException('El descuento es mayor al precio del producto. No se puede aplicar')
        return discount

    def explain_rules(self):
        """Devuelve string que explica las reglas"""
        rules = self.rules.all()
        out= []
        for i, r in enumerate(list(rules)):
            if i: #no se tiene en cuenta conector en regla 1
                con = '<b>Ó</b>' if r.use_or else '<b>y</b>'
                out.append(con)
            out.append("%s"%(r))
        return ' '.join(out)

    class Meta:
        verbose_name = u'Descuento de catálogo' 
        verbose_name_plural = u'Descuentos de catálogo' 


class CatalogDiscountRule(models.Model):

    """Reglas aplicables para descuentos de catalogo. 
    (CatalogDiscount has_many CatalogDiscountRule)
    - Se puede configurar para validar que el producto pertenezca a una categoria. Tipo 1
    - Se puede configurar para validar que el producto sea un producto en especifico. Tipo 2
    por ej: rule.rtype = 1 , rule.category = Category(pk=10) # Regla que aprueba
    productos que pertenecen a la categoria pk=10
    """

    rtype = models.IntegerField(
        "Tipo", choices=((1, 'Categoria'), (2, 'Producto')), default=1)
    discount = models.ForeignKey(CatalogDiscount, related_name='rules')
    category = models.ManyToManyField(Category, null=True, blank=True)
    product = models.ManyToManyField(Product, null=True, blank=True)

    def check_product(self, product):
        """Testea que el producto pase esta regla"""
        if self.rtype == 1:
            # Categoria
            if len(self.category.filter(pk=product.get_first_category().pk)):
                return True
            elif product.get_first_category().parent is not None:
                return len(self.category.filter(pk=product.get_first_category().parent.pk )) > 0

        elif self.rtype == 2:
            # Producto
            return len(self.product.filter(pk=product.pk)) > 0
        return False

    def __unicode__(self):
        txt = u"Categoría"  if self.rtype == 1 else u"Producto"
        return txt

    class Meta:
        verbose_name = u'Regla de catálogo'
        verbose_name_plural = u'Reglas de catálogo'
