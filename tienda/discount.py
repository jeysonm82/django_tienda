from tienda.models import CatalogDiscount
from datetime import datetime as dt


class DiscountMiddleware:

    def get_discounts_qset(self):
        today = dt.today()
        discounts = CatalogDiscount.objects.filter(enabled=True,
                                                   activated_by_coupon=False,
                                                   date_from__lte=today,
                                                   date_to__gte=today, days__contains="%s"%(today.weekday()+1)).prefetch_related('rules', 'rules__category', 'rules__product').order_by('priority') 
        return discounts


    def process_request(self, request):
        """Carga a request los descuentos habilitados y que estan vigentes segun las fechas"""
        request.discounts = self.get_discounts_qset()

    def process_template_response(self, request, response):
        for plist in ('products', 'related_products'):
            self.process_products_list(plist, request, response)
        return response

    def process_products_list(self, key, request, response):
        if response.context_data is not None and key in response.context_data:
            products = list(response.context_data[key])
            for product in products:
                if product.discount is not None:
                    continue
                d = 0
                product.calculate_discount()
            response.context_data[key] = products
