from tienda.models import Product
from collections import OrderedDict

class Cart(object):
    _cart_instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._cart_instance:
            cls._cart_instance = super(Cart, cls).__new__(
                                cls, *args, **kwargs)
        return cls._cart_instance

    def __init__(self, session_storage=None):
        self.storage = OrderedDict({})
        self.session_storage = session_storage

        # Load session_storage
        pids = self.session_storage.keys()
        products = Product.objects.filter(pk__in=pids)
        self.queryset = products
        self.storage = OrderedDict({p: session_storage["%s"%(p.pk)] for p in products})
        Cart._cart_instance = self

    def add(self, product, quantity):
        if quantity == 0:
            self.remove(product)
            return

        if product in self.storage:
            self.storage[product] += quantity
        else:
            self.storage[product] = quantity

        if self.session_storage is not None:
            if u"%s"%(product.pk) in self.session_storage:
                self.session_storage[u"%s"%(product.pk)] += quantity
            else:
                self.session_storage[u"%s"%(product.pk)] = quantity

    def update(self, product, quantity):
        if quantity == 0:
            self.remove(product)
            return

        self.storage[product] = quantity

        if self.session_storage is not None:
            self.session_storage[u"%s"%(product.pk)] = quantity



    def remove(self, product):
        if product in self.storage:
            del self.storage[product]
        
        if self.session_storage is not None and u"%s"%(product.pk) in self.session_storage:
            del self.session_storage[u"%s"%(product.pk)]

    def to_session_storage(self):
        return {u"%s"%(k.pk): v for k, v in self.storage.iteritems()}

    
    def get_total(self):
        return sum([p.get_price() * q for p, q in self.storage.iteritems()]) #TODO discounted price
        
    def __str__(self):
        return "%s"%(self.storage)

SESSION_KEY = 'TIENDA_CART_KEY'

class CartMiddleware(object):

    def process_request(self, request):
        try:
            cart_session_storage = request.session[SESSION_KEY]
        except KeyError:
            cart_session_storage = {}
        setattr(request, 'cart', cart_session_storage)
        setattr(request, 'cart_changed', False)

    def process_response(self, request, response):
        if hasattr(request, 'cart'):
            request.session[SESSION_KEY] = request.cart
        return response

    def process_template_response(self, request, response):
        if response.context_data is not None and hasattr(request, 'cart'):
            response.context_data['total_cart_entries'] = sum([int(x) for k,x in request.cart.iteritems()])
        return response
