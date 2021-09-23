from rest_framework import serializers
from kitchen.models import Reviews, Kitchens, Categories, UserDiscountCoupons, Items, Menus
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

class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = ['id', 'category', 'itemName', 'itemType', 'price', 'image', 'condition', 'itemDesc']

class MenuSerializer(serializers.ModelSerializer):
    item = ItemsSerializer(read_only=True)
    class Meta:
        model = Menus
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'