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
        verbose_name_plural = 'categories'


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


class Product(models.Model):
    name = models.CharField('name', max_length=128)
    description = models.TextField('description', blank=True, default='')
    price = models.DecimalField('price', max_digits=12, decimal_places=2)
    uid = models.CharField('Ref', max_length=32, unique=True)
    categories = models.ManyToManyField(Category, related_name='products')
    attributes = models.ManyToManyField('ProductAttribute', related_name='products', blank=True)
    updated_at = models.DateTimeField('updated at', auto_now=True, null=True)
    enabled = models.BooleanField('enabled', default=True)

    objects = ProductManager()

    def __str__(self):
        return self.name

    def get_first_category(self):
        return self.categories.filter(visible=True).first()

    def __hash__(self):
        return hash((self.pk, self.name))

    def __eq__(self, other):
        return (self.pk, self.name) == (other.pk, other.name)

    def get_price(self):
        return self.price

    def get_slug(self):
        return slugify(smart_text(unidecode(self.name)))

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

class CategoryImage(models.Model):
    category = models.ForeignKey(Category, related_name='images')
    image = VersatileImageField(
        upload_to='categories', ppoi_field='ppoi', blank=False)
    ppoi = PPOIField()
    alt = models.CharField('short description', max_length=128, blank=True)


