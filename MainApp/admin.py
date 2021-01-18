from django.contrib import admin
from .models import User, Addresses, Order

admin.site.register(User)
admin.site.register(Addresses)
admin.site.register(Order)
