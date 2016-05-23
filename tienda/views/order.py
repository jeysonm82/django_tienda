from django.views.generic import TemplateView, FormView, View, RedirectView
from tienda.views.checkout import Checkout, SESSION_KEY

class CreateOrderView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        Checkout.request = self.request

        checkout = Checkout(self.request.session[SESSION_KEY])
        order = checkout.create_order()
        import pdb
        pdb.set_trace()
        """
        try:
        except:
            url = '/'
        else:
            url = '/view-order/%s/'%(order.token)
        return url"""
        return None
