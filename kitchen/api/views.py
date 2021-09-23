from django.db.models.fields import NullBooleanField
from rest_framework.response import Response
from django.contrib.auth import login, logout, authenticate
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from kitchen.models import Kitchens, Reviews, Categories, Menus, Items, SubItems, Reviews, UserDiscountCoupons, ComplaintsAndRefunds
from MainApp.models import FavouriteKitchens, Addresses, User, FavouriteKitchens, Order
from .serializers import AddressSerializer, ItemsSerializer, OrderSerializer, UserSerializer, KitchensSerializer, MenuSerializer, CategorySerializer
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
		ordersjson.update({'customer': UserSerializer(i.customer).data})
		ordersjson.update({'delivery_addr': AddressSerializer(i.delivery_addr).data})
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
	if "msgtocust" in request.data.keys():
		msgtocust = request.data['msgtocust']
	order = Order.objects.filter(id=orderid)

	if status == "Cancelled":
		if order[0].coupon_id != None and order[0].coupon.user != None:
			update_coupon(order[0].coupon_id, False)
		if order[0].amount_paid > 0:
			refundStatus = "Under Process"
			issue = "The Order was Cancelled by Kitchen."
			comments = msgtocust
			subject = "Refund"
			raise_refund_request(order[0].kitchen, order[0], order[0].customer, comments, issue, refundStatus, order[0].customer.phone, subject)

	if "msgtocust" in request.data.keys():
		res = order.update(status=status, completed_at=currentDate, msgtocust=msgtocust)
	else:
		res = order.update(status=status, completed_at=currentDate)

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


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def handleNewOrder(request):
	context = {}
	currentDate = getCurrentDate()
	orderid = request.data['orderid']
	action = request.data['action']
	msgtocust = request.data['msgtocust']
	order = Order.objects.filter(id=orderid)[0]
	if action == "Accept":
		if request.user.kitchens.wantAdvancePayment:
			status = "Payment"
		else:
			status = "Placed"
	else:
		status = "Rejected"

	if status == "Payment" or status == "Placed":
		if order.coupon_id != None and order.coupon.user != None:
			update_coupon(order.coupon_id, True)

	if status == "Rejected":
		if order.coupon_id != None and order.coupon.user != None:
			update_coupon(order.coupon_id, False)
	
	Order.objects.filter(id=orderid).update(status=status, completed_at=currentDate, msgtocust=msgtocust)
	context['response'] = "Order " + status
	
	return Response(context)


def update_coupon(couponId, redeemed):
	UserDiscountCoupons.objects.filter(id=couponId).update(redeemed=redeemed)


def raise_refund_request(kitchen, order, cust, comments, issue, refundStatus, paytmNo, subject):
	currentDate = getCurrentDate()
	ComplaintsAndRefunds.objects.create(kit=kitchen, order=order, user=cust, comments=comments, issue=issue, status=refundStatus, paytmNo=paytmNo, request_date=currentDate, subject=subject)


@api_view(['POST'])
def getOrder(request):
	context = {}
	orderid = request.data['orderid']
	order = Order.objects.filter(id=orderid)[0]
	orderjson = OrderSerializer(order).data
	orderjson.update({'customer': UserSerializer(order.customer).data})
	orderjson.update({'delivery_addr': AddressSerializer(order.delivery_addr).data})
	context = {
		'order': orderjson
	}
	return Response(context)


@api_view(['POST'])
def updateMessageToCustomer(request):
	context = {}
	orderid = request.data['orderid']
	msgtocust = request.data['msgtocust']
	res = Order.objects.filter(id=orderid).update(msgtocust=msgtocust)
	if res == 1:
		context['response'] = "Message updated Successfully"
	else:
		context['response'] = "Message not updated. Try again."
	return Response(context)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def handleKitchenStatus(request):
	context = {}
	action = request.data['action']
	if action == "changeStatus":
		if request.user.kitchens.status == "Open":
			status = "Closed"
		else:
			status = "Open"
		Kitchens.objects.filter(id=request.user.kitchens.id).update(status=status)
	kitchen = Kitchens.objects.filter(id=request.user.kitchens.id)[0]
	kitjson = KitchensSerializer(kitchen).data
	context['kitchen'] = kitjson
	return Response(context)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def handleMenu(request):
	context = {}
	action = request.data['action']

	if action == "updateitem":
		itemid = request.data['itemid']
		itemstatus = request.data['itemstatus']
		offer = request.data['offer']
		minOrder = request.data['minOrder']
		Menus.objects.filter(id=itemid).update(out_of_stock=itemstatus, offer=offer, minOrder=minOrder)
	elif action == "removeitem":
		itemid = request.data['itemid']
		Menus.objects.filter(id=itemid).delete()

	categories = Categories.objects.filter(kit=request.user.kitchens)
	categoryjson = CategorySerializer(categories, many=True).data
	menu = Menus.objects.filter(kit=request.user.kitchens)
	menujson = MenuSerializer(menu, many=True).data
	context = {
		'menu': menujson,
		'categories': categoryjson
	}
	return Response(context)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def addMenuItems(request):
	context = {}
	action = request.data['action']
	if action == "fetch":
		allItems = Items.objects.filter(kit=request.user.kitchens)
		allItemsJson = ItemsSerializer(allItems, many=True).data
		menu = Menus.objects.filter(kit=request.user.kitchens)
		menujson = MenuSerializer(menu, many=True).data
		categories = Categories.objects.filter(kit=request.user.kitchens)
		categoryjson = CategorySerializer(categories, many=True).data
		context = {
			'allItems': allItemsJson,
			'menuItems': menujson,
			'categories': categoryjson
		}
	elif action == "add":
		itemsIds = request.data['itemsIds']
		for id in itemsIds:
			Menus.objects.create(item_id=id, kit=request.user.kitchens)
		context['response'] = "Successfully added"
	return Response(context)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def fetchUser(request):
	user = request.user
	userjson = UserSerializer(user).data
	context = {
		'user': userjson,
	}
	return Response(context)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def handleAllItems(request):
	context = {}
	action = request.data['action']
	if action == "deleteItem":
		itemid = request.data['itemid']
		Items.objects.filter(id=itemid).delete()
	allItems = Items.objects.filter(kit=request.user.kitchens)
	allItemsJson = ItemsSerializer(allItems, many=True).data
	categories = Categories.objects.filter(kit=request.user.kitchens)
	categoryjson = CategorySerializer(categories, many=True).data
	context = {
		'allItems': allItemsJson,
		'categories': categoryjson
	}
	return Response(context)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def addNewItem(request):
	context = {}
	action = request.data['action']

	if action == "addNewCategory":
		newCategory = request.data['newCategory']
		Categories.objects.create(category=newCategory, kit=request.user.kitchens)
		action = "fetchCategories"
	elif action == "deleteCategory":
		categoryid = request.data['selectedCategory']
		Categories.objects.filter(id=categoryid).delete()
		action = "fetchCategories"

	if action == "fetchCategories":
		categories = Categories.objects.filter(kit=request.user.kitchens)
		categoryjson = CategorySerializer(categories, many=True).data
		context = {
			'categories': categoryjson
		}

	if action == "addNewItem":
		form = ItemsSerializer(data=request.data)
		if form.is_valid():
			iteminstance = form.save(kit=request.user.kitchens)
			iteminstance.save()
			context = {
				'itemid': iteminstance.id,
				'response': "Item Added Successfully"
			}
		else:
			context = form.errors
	return Response(context)


@api_view(['POST'])
def fetchItem(request):
	context = {}
	itemid = request.data['itemid']
	item = Items.objects.filter(id=itemid)[0]
	itemjson = ItemsSerializer(item).data
	context['item'] = itemjson
	return Response(context)