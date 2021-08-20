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
        fields = ['id', 'phone', 'email', 'first_name', 'last_name', 'username']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addresses
        fields = ['id', 'place', 'latitude', 'longitude', 'address', 'floorNo']

class KitchensSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kitchens
        fields = '__all__'