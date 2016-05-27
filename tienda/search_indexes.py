from haystack import indexes
import datetime
from tienda.models import Product

class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)
    enabled = indexes.BooleanField(model_attr='enabled')
    #categories = indexes.CharField(model_attr='categories')

    def get_model(self):
        return Product

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(updated_at__lte=datetime.datetime.now())
