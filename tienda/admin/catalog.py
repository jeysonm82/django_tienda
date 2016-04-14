from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from tienda.models import CategoryImage, Category

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
