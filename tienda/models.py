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
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.utils.timezone import now
from uuid import uuid4
from django.conf import settings

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
        verbose_name = u'categoría'
        verbose_name_plural = u'categorías'


class ProductManager(models.Manager):

    """ Product manager for product for table level operations """
    with_prefecth = True

    def get_queryset(self):
        if ProductManager.with_prefecth:
            return super(ProductManager, self).get_queryset().prefetch_related(*(("categories", "images")+settings.PRODUCT_PREFECTH_MODELS))
        return super(ProductManager, self).get_queryset()

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

    def all_noprefetch(self):
        ProductManager.with_prefecth = False
        qset = self.all()
        ProductManager.with_prefecth = True
        return qset

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
    name = models.CharField('Nombre', max_length=128)
    description = models.TextField(u'Descripción', blank=True, default='')
    price = models.DecimalField(u'Precio', max_digits=12, decimal_places=2)
    uid = models.CharField(u'Referencia', max_length=32, unique=True)
    categories = models.ManyToManyField(Category, related_name='products')
    tax = models.DecimalField(u"Impuesto", max_digits=3, decimal_places=1, default=0)
    attributes = models.ManyToManyField('ProductAttribute', related_name='products', blank=True)
    updated_at = models.DateTimeField('updated at', auto_now=True, null=True)
    enabled = models.BooleanField(u'Habilitado', default=True)
    discount = None
    discount_value = 0
    objects = ProductManager()
    search = ProductSearchManager()
    
    def __unicode__(self):
        return self.name

    def get_first_category(self):
        #return self.categories.filter(visible=True).first()
        qset = self.categories.all()
        if qset:
            return qset[0]
    
    def get_first_image(self):
        qset = self.images.all()
        if qset:
            return qset[0]

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
    
    def calculate_discount(self, discounts=[]):
      d = 0
      if self.discount is not None:
        return self.discount_value

      ProductManager.with_prefecth = False
      #with_prefecth = false to avoid related product models from CatalogDiscountRule.product to
      #unnecessarily prefetch related models.
      for discount in discounts:
        try:
            d = discount.check_product(self)
        except:
            pass
        else:
            self.discount = discount
            self.discount_value = d
            ProductManager.with_prefecth = True
            return d # TODO only one discount

      ProductManager.with_prefecth = True
      return 0

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

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
        verbose_name = 'Imagen de producto'
        verbose_name_plural = 'Imágenes de producto'

class CategoryImage(models.Model):
    category = models.ForeignKey(Category, related_name='images')
    image = VersatileImageField(
        upload_to='categories', ppoi_field='ppoi', blank=False)
    ppoi = PPOIField()
    alt = models.CharField('short description', max_length=128, blank=True)


    class Meta:
        verbose_name = u"Imagen de categoría"
        verbose_name_plural = u"Imágenes de categoría"

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
        for i, rule in enumerate(self.rules.all()):
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
        for i, r in enumerate(rules):
            if i: #no se tiene en cuenta conector en regla 1
                con = '<b>Ó</b>' if r.use_or else '<b>y</b>'
                out.append(con)
            out.append("%s"%(r))
        return ' '.join(out)
    
    def get_products_queryset(self):
        """Get all products affected by this discount"""
        queryset = Product.objects.none()
        for i, rule in enumerate(self.rules.all()):
            if rule.rtype == 1:
                qset = Product.objects.filter(categories__in=rule.category.all(), enabled=True)
            elif rule.rtype == 2:
                qset = rule.product.filter(enabled=True)
            queryset |= qset
        queryset = queryset.distinct()
        return queryset

    def get_cats_queryset(self):
        """Get all categories affected by this discount"""
        queryset = Category.objects.none()
        for i, rule in enumerate(self.rules.all()):
            if rule.rtype == 1:
                qset = rule.category.all()
            elif rule.rtype == 2:
                qset = Category.objects.filter(products__in=rule.product.all_noprefetch())
            queryset |= qset
        queryset = queryset.distinct()
        return queryset


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
            pcat = product.get_first_category()
            #if len(self.category.filter(pk=pcat.pk)):
            if pcat in self.category.all():
                return True
            elif pcat.parent is not None:
                return len(self.category.filter(pk=pcat.parent.pk )) > 0

        elif self.rtype == 2:
            # Producto
            return product in self.product.all()
            #return len(self.product.filter(pk=product.pk)) > 0
        return False

    def __unicode__(self):
        txt = u"Categoria"  if self.rtype == 1 else u"Producto"
        return txt

    class Meta:
        verbose_name = u'Regla de catálogo'
        verbose_name_plural = u'Reglas de catálogo'

class Address(models.Model):
    title = models.CharField(u"Título", max_length=256)
    first_name = models.CharField("Nombre",max_length=256)
    last_name = models.CharField('Apellido', max_length=256)
    street_address_1 = models.CharField(u'Dirección', max_length=256)
    street_address_2 = models.CharField(u'Dirección 2', max_length=256, blank=True, default='')
    city = models.CharField('Ciudad', max_length=256)
    city_area = models.CharField('Barrio', max_length=128)
    phone = models.IntegerField(u'Teléfono')
    mobile = models.IntegerField(u'Celular')

    def __unicode__(self):
        #return "%s - %s"%(self.title, self.street_address_1)
        return "%s, %s"%(self.street_address_1, self.city)

    def full_address(self):
        return u"Dirección: %s, %s. Teléfono: %s. Celular: %s. Destinatario: %s "%(self.street_address_1, self.city, self.phone, self.mobile, self.first_name + " " + self.last_name)

    class Meta:
        verbose_name = u"Dirección"
        verbose_name_plural = u"Direcciones"

class UserManager(BaseUserManager):

    def create_user(self, email, password, name, last_name, gov_id, **extra_fields):
        email = UserManager.normalize_email(email)
        user = StoreUser(username=email, email=email, first_name=name, last_name=last_name, gov_id=gov_id,  is_active=True,
                          is_staff=False, **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

class StoreUser(User):
    gov_id = models.IntegerField(u'Documento de identidad', null=True)
    addresses = models.ManyToManyField(Address, blank=True)
    default_shipping_address = models.ForeignKey(Address,related_name='+',
            verbose_name="Default shipping address", null=True, blank=True, on_delete=models.SET_NULL)
    objects = UserManager()

    def default_address(self):
        return self.addresses.first()
    def __unicode__(self):
        return "%s %s (Documento: %s)"%(self.first_name, self.last_name, self.gov_id)

class OrderManager(models.Manager):

    def create_order(self,user, shipping_address, shipping_method, payment_method, cart_storage, discounts=None):
        """
        shipping_method: ShippingMethod instance (with address)
        payment_method: PaymentMethod instance 
        """

        order = Order()
        order.user = user
        order.shipping_method = shipping_method.ref
        order.shipping_address = shipping_address
        order.shipping_price = shipping_method.calculate()

        payment = Payment()
        payment.method = payment_method.ref
        payment.payment_ref = payment_method.payment_ref

        applied_discounts = set()
        total = 0

        p_orders = []
        for p, q in cart_storage.iteritems():
            p_order = ProductOrder()
            p_order.product = p
            p_order.product_name = p.name
            p_order.product_uid = p.uid
            p_order.quantity = q
            p_order.price = p.price
            p_order.tax = p.tax

            p_order.discount_price = 0
            try:
                p_order.discount_price = p.calculate_discount(discounts)
            except:
                pass
            p_orders.append(p_order)

            if p.discount is not None:
                applied_discounts.add(p.discount)
            total += (p_order.price - p_order.discount_price)  * p_order.quantity

        order.discounts = ', '.join(["%s (id: %s)"%(d.name, d.pk) for d in applied_discounts])
        total += order.shipping_price
        order.total = total
        order.status = Order.NEW
        order.token = str(uuid4())
        # Save stuff
        order.save()
        payment.order = order
        for po in p_orders:
            po.order = order
            po.save()
        payment.save()

        return order


class Order(models.Model):

    NEW = 'new'
    CANCELLED = 'cancelled'
    SHIPPED = 'shipped'
    PAYMENT_PENDING = 'payment-pending'
    FULLY_PAID = 'fully-paid'
    STATUS_CHOICES = [(NEW, "En proceso"),
        (CANCELLED, 'Cancelada'),
        (SHIPPED, 'Enviada'),
        (PAYMENT_PENDING, 'Pendiente de pago'),
        (FULLY_PAID, 'Pagada')]

    created = models.DateTimeField(default=now, editable=False)
    status = models.CharField(u"Estado", choices=STATUS_CHOICES, max_length=30);
    user = models.ForeignKey(StoreUser, null=True, blank=True)
    token = models.CharField(u"Token", max_length=36, unique=True, editable=False)
    shipping_method = models.CharField(u"Método de envío", max_length=30)
    shipping_address = models.ForeignKey(Address, null=True, editable=False, verbose_name=u'Dirección de envío')
    shipping_price = models.DecimalField(u"Valor domicilio",  max_digits=12, decimal_places=2)
    total = models.DecimalField(u"Total",  max_digits=12, decimal_places=2)
    discounts = models.CharField(u"Descuentos aplicados", max_length=100, blank=True, null=True)
    obs = models.TextField(u"Observaciones", null=True, blank=True)
    extra = models.CharField(u"Información adicional de órden", max_length=100, default="-")
    objects = OrderManager()

    def __unicode__(self):
        return "PED-%s"%(self.token[:8].upper())

    def ref(self):
        return "PED-%s"%(self.token[:8].upper())

    def recalculate_order(self):
        pass
    
    def full_address(self):
        return self.shipping_address.full_address()
    full_address.short_description = "Datos de envio"

    class Meta:
        verbose_name = u"Órden"
        verbose_name_plural = u"Órdenes"
        ordering = ['-status', '-pk']


class ProductOrder(models.Model):
    order = models.ForeignKey(Order, related_name='products')
    product = models.ForeignKey(Product, null=True, blank=True)
    product_name = models.CharField(u"Nombre", max_length=100)
    product_uid = models.CharField(u"Ref", max_length=32)
    quantity = models.IntegerField(u"Cantidad")
    price = models.DecimalField(u"Precio",  max_digits=12, decimal_places=2)
    discount_price = models.DecimalField(u"Descuento", default=0,  max_digits=12, decimal_places=2)
    tax = models.DecimalField(u"Impuesto", default=0,  max_digits=12, decimal_places=2)

    def __unicode__(self):
        return "%s. Cantidad: %s, Precio Unitario: %s"%(self.product_name, self.quantity, self.price - self.discount_price)

    class Meta:
        verbose_name = u"Producto de órden"
        verbose_name_plural = u"Productos de órden"


class Payment(models.Model):
    STATUS_CHOICES = [ (Order.PAYMENT_PENDING, 'Pendiente de pago'),
        (Order.FULLY_PAID, 'Pagada'), (Order.CANCELLED, 'Cancelado')]
    order = models.ForeignKey(Order, related_name='payments')
    method = models.CharField(u"Método de pago", max_length=30, choices=settings.PAYMENT_METHOD_CHOICES)
    payment_ref = models.CharField(u"Referencia de pago", max_length=50)
    total = models.DecimalField(u"Valor",default=0,  max_digits=12, decimal_places=2)
    status = models.CharField(u"Estado", choices=STATUS_CHOICES, max_length=30, default=Order.PAYMENT_PENDING)

    class Meta:
        verbose_name = u"Pago"
        verbose_name_plural = u"Pagos"
