from tienda.models import Product
from collections import OrderedDict

class Cart(object):

    def __init__(self, session_storage=None):
        self.storage = OrderedDict({})
        self.session_storage = session_storage

        # Load session_storage
        pids = self.session_storage.keys()
        products = Product.objects.filter(pk__in=pids)
        self.storage = OrderedDict({p: session_storage["%s"%(p.pk)] for p in products})

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
        return sum([p.get_price() * q for p, q in self.storage.iteritems()])
        
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

    def process_response(self, request, response):
        if hasattr(request, 'cart'):
            request.session[SESSION_KEY] = request.cart
        return response
