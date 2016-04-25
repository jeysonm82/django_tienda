from saleor.more.models import CatalogDiscount
from datetime import datetime as dt
from saleor.cart import Cart
from django.db.models import Q


class DiscountMiddleware:

    def process_request(self, request):
        """Carga a request los descuentos habilitados y que estan vigentes segun las fechas"""
        
        today = dt.today()
        discounts = CatalogDiscount.objects.filter(enabled=True,
                                                   activated_by_coupon=False,
                                                   date_from__lte=today,
                                                   date_to__gte=today, days__contains="%s"%(dt.weekday()+1)).prefetch_related('rules').order_by('priority') 

        request.discounts = discounts

    def process_template_response(self, request, response):
        if 'products' in response.context_data:
            products = list(response.context_data['products'])
            for product in products:
                d = 0
                for discount in request.discounts:
                    try:
                        d = discount.check_product(product)
                    except:
                        pass
                    else:
                        break #TODO only one discount per product
                product.discount = discount
                product.discount_value = d
            response.context_data['products'] = products
        return response
