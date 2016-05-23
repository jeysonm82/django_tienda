from django.views.generic import TemplateView, FormView, View, RedirectView, DetailView
from tienda.views.checkout import Checkout, SESSION_KEY
from django.core.urlresolvers import reverse_lazy
from tienda.models import Order

TOKEN_PATTERN = ('(?P<token>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}'
                 '-[0-9a-z]{12})')

class CreateOrderView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        Checkout.request = self.request
        try:
            checkout = Checkout(self.request.session[SESSION_KEY])
            checkout.user = self.request.user.storeuser
            order = checkout.create_order()
        except Exception as e:
            url = reverse_lazy('checkout')
            print "ERROR", e
        else:
            url = reverse_lazy('view-order', kwargs={'token': order.token})
        return url


class OrderDetailView(DetailView):
    model = Order


    def get_object(self):
        return Order.objects.get(token=self.kwargs['token'])
