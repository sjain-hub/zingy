from django.db.models.fields import NullBooleanField
from rest_framework.response import Response
from django.contrib.auth import login, logout, authenticate
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from kitchen.models import Kitchens, Reviews, Categories, Menus, Items, SubItems, Reviews, UserDiscountCoupons
from MainApp.models import FavouriteKitchens, Addresses, User, FavouriteKitchens, Order
from .serializers import OrderSerializer, UserSerializer
from django.contrib.gis.geos import Point
from django.db.models import Avg, Q
from datetime import datetime, timedelta
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from django.contrib.auth.models import update_last_login
import json
import re
from MainApp import FCMManager as fcm


def getCurrentDate():
	return datetime.now()


@api_view(['POST'])
def login(request):
	context = {}
	username = request.data['username']
	password = request.data['password']
	user = authenticate(username=username,password=password)
	if user is not None and user.is_kitchen:
		if user.is_active:
			update_last_login(None, user)
			token = Token.objects.get(user=user)
			context['token'] = token.key
		else:
			raise APIException("Your Account is Disabled")
	else:
		raise APIException("Invalid Login")
	return Response(context)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def orderList(request):
	context = {}
	todaysDate = getCurrentDate().date()
	day = request.data['day']
	if day == "today":
		orders = Order.objects.filter(kitchen_id=request.user.kitchens.id, scheduled_order=todaysDate).order_by("scheduled_order")
	orders_object = []
	for i in orders:
		ordersjson = OrderSerializer(i).data
		ordersjson.update({'cust': UserSerializer(i.customer).data})
		orders_object.append(ordersjson)
	context = {
		'orders': orders_object
	}
	return Response(context)