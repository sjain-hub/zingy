from rest_framework import serializers
from kitchen.models import Reviews, Kitchens, Categories, UserDiscountCoupons
from MainApp.models import User, Addresses, Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'email', 'first_name', 'last_name', 'username']