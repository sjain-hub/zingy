from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Addresses, Order, FavouriteKitchens, Queries


admin.site.register(Addresses)
admin.site.register(FavouriteKitchens)

class Users(UserAdmin):
    list_display = ('id', 'first_name', 'last_name', 'is_customer', 'is_kitchen')
    search_fields = ('id', 'first_name', 'last_name', 'phone')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
admin.site.register(User, Users)

class AllOrders(admin.ModelAdmin):
    list_display = ('id', 'customer', 'kitchen', 'total_amount', 'status')
    search_fields = ('id', 'customer__username', 'kitchen__kitName')
admin.site.register(Order, AllOrders)

class KitchenQueries(admin.ModelAdmin):
    list_display = ('name', 'phone', 'subject', 'resolved')
    search_fields = ('phone', 'name')
admin.site.register(Queries, KitchenQueries)