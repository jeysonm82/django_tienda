# -*- coding: utf-8 -*-
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from tienda.models import CategoryImage, Category, CatalogDiscount, CatalogDiscountRule, Product
from django import forms

class CategoryImageInline(admin.TabularInline):
    model = CategoryImage
    extra = 2
    max_entries = 2
    max_num = 2
    can_delete = True


class CategoryAdmin(MPTTModelAdmin):
    list_display = ('tabbed_name', )
    inlines = [CategoryImageInline]

    def tabbed_name(self, obj):
        return 2 * '<i class="fa fa-minus "></i>' * obj.level + ' ' + obj.name
    tabbed_name.allow_tags = True
    tabbed_name.short_description = Category._meta.verbose_name


class CustomFilteredSelectMultiple(admin.widgets.FilteredSelectMultiple):
    """Custom filtered box that filters the options by querying a REST API. Useful when the options list is large (>1000)"""
    @property
    def media(self):
        js = ["core.js", "SelectFilter2.js"]
        #Custom SelectBox is implemented in filtered_select_multiple_products
        fm = forms.Media(js=["admin/js/%s" % path for path in js] + ["js/filtered_select_multiple_products.js"])
        return fm


class CatalogDiscountRuleForm(forms.ModelForm):
    product = forms.ModelMultipleChoiceField(queryset=Product.objects.none(), required=False, widget=CustomFilteredSelectMultiple("Productos", is_stacked=False))

    def __init__(self, *args, **kwargs):
        super(CatalogDiscountRuleForm, self).__init__(*args, **kwargs)
        if 'data' in kwargs:
            # We're posting
            self.fields['product'].queryset = Product.objects.all_noprefetch()
        else:
            if self.instance.pk:
                self.fields['product'].queryset = self.instance.product.all_noprefetch() #Product.objects.all_noprefetch()
                    
        pass

    class Meta:
        Model=CatalogDiscountRule

class CatalogDiscountRuleInline(admin.StackedInline):
    model = CatalogDiscountRule
    form=CatalogDiscountRuleForm
    extra = 0
    fields = ['rtype', 'category', 'product']
    filter_horizontal = ('category','product')

class DaysSelectorWidget(forms.CheckboxSelectMultiple):
    DAYS = ((1, 'Lunes'),(2, 'Martes'),(3, 'Miércoles'), (4, 'Jueves'),
            (5, 'Viernes'),(6, 'Sábado'),(7, 'Domingo'))

    def __init__(self, attrs=None, choices=()):
        super(DaysSelectorWidget, self).__init__(attrs, self.DAYS)

    def render(self,  name, value, attrs=None, choices=()):
        value = [] if isinstance(value, str) else value
        html = super(DaysSelectorWidget, self).render(name, value, attrs, choices)
        return html

    def value_from_datadict(self, data, files, name):
        # Returns string instead of list
        return ','.join( data.getlist(name))

class CatalogDiscountForm(forms.ModelForm):

    class Meta:
        model = CatalogDiscount
        exclude = ('activated_by_coupon', 'coupon')
        widgets = {'days': DaysSelectorWidget(),}


class CatalogDiscountAdmin(admin.ModelAdmin):
    model = CatalogDiscount
    inlines = [CatalogDiscountRuleInline]
    change_form_template = 'tienda/change_form.html'
    list_display = ('id', 'name', 'description', 'discount', 'discount_unit', 'date_from', 'date_to', 'days_formatted', 'enabled')
    list_display_links = ('id', 'name')
    form = CatalogDiscountForm


    def days_formatted(self, obj):
        return ', '.join([DaysSelectorWidget.DAYS[int(x)-1][1] for x in obj.days.split(',')])

    days_formatted.short_description = u"Días"
