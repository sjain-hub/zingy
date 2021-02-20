from django.contrib import admin
from .models import Kitchens, Items, SubItems, Menus, Categories, Reviews, PaymentHistory, PlanList, ComplaintsAndRefunds, UserDiscountCoupons

admin.site.register(Categories)
admin.site.register(Items)
admin.site.register(SubItems)
admin.site.register(Menus)
admin.site.register(Reviews)
admin.site.register(PlanList)
admin.site.register(UserDiscountCoupons)


class AllKitchens(admin.ModelAdmin):
    list_display = ("kitName", "user", "city", "approved")
    search_fields = ('kitName', 'user__username', 'city')
admin.site.register(Kitchens, AllKitchens)

class Complaints(admin.ModelAdmin):
    list_display = ('id', 'order', 'kit', 'user', 'status')
    search_fields = ('kit__kitName', 'user__username', 'order__id')
admin.site.register(ComplaintsAndRefunds, Complaints)

class KitchenPaymentHistory(admin.ModelAdmin):
    list_display = ('id', 'kit', 'user', 'pack_name', 'status')
    search_fields = ('kit__kitName', 'user__username')
admin.site.register(PaymentHistory, KitchenPaymentHistory)
