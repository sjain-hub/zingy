from rest_framework import serializers
from kitchen.models import Reviews, Kitchens, Categories, Reviews, UserDiscountCoupons
from MainApp.models import User, Addresses

class KitchensSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kitchens
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'email', 'first_name', 'last_name', 'username']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Reviews
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addresses
        fields = '__all__'


class CouponsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDiscountCoupons
        fields = '__all__'