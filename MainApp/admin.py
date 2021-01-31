from django.contrib import admin
from .models import User, Addresses, Order, FavouriteKitchens

admin.site.register(User)
admin.site.register(Addresses)
admin.site.register(Order)
admin.site.register(FavouriteKitchens)
