from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import Kitchens, Items, SubItems, Menus, Categories, Reviews, PaymentHistory, PlanList

admin.site.register(Categories)
admin.site.register(Items)
admin.site.register(SubItems)
admin.site.register(Menus)
admin.site.register(Reviews)
admin.site.register(PaymentHistory)
admin.site.register(PlanList)

@admin.register(Kitchens)
class ShopAdmin(OSMGeoAdmin):
    list_display = ("kitName", "user", "city", "approved")
