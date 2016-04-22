# -*- coding: utf-8 -*-
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from tienda.models import CategoryImage, Category, CatalogDiscount #, CatalogDiscountRule
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

'''
class CatalogDiscountRuleInline(admin.StackedInline):
    model = CatalogDiscountRule
    extra = 1
    fields = ['use_or', 'rtype', 'category', 'product']
'''

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
    #inlines = [CatalogDiscountRuleInline]
    #change_form_template = 'more/admin/change_form.html'
    list_display = ('id', 'name', 'description','date_from', 'date_to', 'enabled')
    list_display_links = ('id', 'name')
    form = CatalogDiscountForm
