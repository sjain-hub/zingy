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
	day = request.data['day']
	if day == "today":
		date = getCurrentDate()
		minDate = date.replace(hour=0, minute=0)
		maxDate = date.replace(hour=23, minute=59)
		orders = Order.objects.filter(kitchen_id=request.user.kitchens.id, scheduled_order__gte=minDate, scheduled_order__lte=maxDate).order_by("scheduled_order")
	elif day == "tomorrow":
		date = getCurrentDate() + timedelta(days=1)
		minDate = date.replace(hour=0, minute=0)
		maxDate = date.replace(hour=23, minute=59)
		orders = Order.objects.filter(kitchen_id=request.user.kitchens.id, scheduled_order__gte=minDate, scheduled_order__lte=maxDate).order_by("scheduled_order")
	elif day == "day-after-tomorrow":
		date = getCurrentDate() + timedelta(days=2)
		minDate = date.replace(hour=0, minute=0)
		maxDate = date.replace(hour=23, minute=59)
		orders = Order.objects.filter(kitchen_id=request.user.kitchens.id, scheduled_order__gte=minDate, scheduled_order__lte=maxDate).order_by("scheduled_order")
	elif day == "all":
		orders = Order.objects.filter(kitchen_id=request.user.kitchens.id, status="Waiting").order_by("scheduled_order")

	orders_object = []
	for i in orders:
		ordersjson = OrderSerializer(i).data
		ordersjson.update({'cust': UserSerializer(i.customer).data})
		orders_object.append(ordersjson)
	context = {
		'orders': orders_object
	}
	return Response(context)


@api_view(['POST'])
def changeOrderStatus(request):
	context = {}
	currentDate = getCurrentDate()
	orderid = request.data['orderid']
	status = request.data['status']
	res = Order.objects.filter(id=orderid).update(status=status, completed_at=currentDate)
	if res == 1:
		context['response'] = "Status updated Successfully"
	else:
		context['response'] = "Order status not updated. Try again."
	return Response(context)


@api_view(['POST'])
def updatePayment(request):
	context = {}
	orderid = request.data['orderid']
	amountPaid = request.data['amountpaid']
	balAmount = request.data['balamount']
	res = Order.objects.filter(id=orderid).update(amount_paid=amountPaid, balance=balAmount)
	if res == 1:
		context['response'] = "Payment updated Successfully"
	else:
		context['response'] = "Payment status not updated. Try again."
	return Response(context)