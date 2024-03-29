from django.db.models.fields import NullBooleanField
from rest_framework.response import Response
from django.contrib.auth import login, logout
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from kitchen.models import Kitchens, Reviews, Categories, Menus, Items, SubItems, Reviews, UserDiscountCoupons, ComplaintsAndRefunds
from MainApp.models import FavouriteKitchens, Addresses, User, FavouriteKitchens, Order
from .serializers import KitchensSerializer, CategorySerializer, ReviewSerializer, AddressSerializer, CouponsSerializer, UserSerializer, OrderSerializer, MenuSerializer, SubItemsSerializer
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
from django.utils import dateparse


tokens = ["dDNsYEH3T6-Swao2uFmft5:APA91bFBoLeTBLy5q0B5d-V3lX9Ye-bNn2M3LCh7_Ia2vvBd6CKDK-PkfrLFQ6Qt7l5A5__otYBH1uBXfuGK3x1zDHyB8mQRmYj0RQSv8gz7SKiAPpoBXqPuF6-ow1L8vDlsSHphcc-b", "dDSUrXzROcFD5ICjWZbC48:APA91bEaGRE9tqViTnCclZ_-Crro7HsqMi6StB4hOClckBV8noDVVwlDtaugUL71uwH61e5IxCFhGUS25gqXZL7zxHT5LM37E53IPwpzsAvpwKmZF2a1kK1ti3Mns4BhbHwP8PDo1wcC"]


regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'


def sendNotification():
	fcm.sendPush("Hi", "This is my next msg", tokens)


def getCurrentDate():
	return datetime.now()


def checkEmail(email):
    if(re.search(regex, email)):
        return True
    else:
        return False


@api_view(['GET'])
def index(request):
	kit_object = Kitchens.objects.filter(approved=True)
	serializer = KitchensSerializer(kit_object, many=True)
	return Response(serializer.data)


@api_view(['POST'])
def nearbyKitchens(request):
	currentDate = getCurrentDate()
	longitude = request.data['lon']
	latitude = request.data['lat']
	user_location = Point(float(longitude), float(latitude), srid=4326)
	kitchens = Kitchens.objects.filter(approved=True)
	kit_object = []
	for i in kitchens:
		dist = user_location.distance(i.location) * 100
		if dist <= 10:
			kitjson = KitchensSerializer(i).data
			kitCoupons = UserDiscountCoupons.objects.filter(Q(user=None), kit=i, redeemed=False, validTill__gte=currentDate)
			maxDiscount = 0
			if kitCoupons:
				maxDiscount = max(coup.discount for coup in kitCoupons)
			kitjson.update({'maxDiscount': maxDiscount})
			catdesc = ""
			categories = Categories.objects.filter(kit_id=i.id)
			for cat in categories:
				catdesc = catdesc + cat.category + ", "
			kitjson.update({'catdesc': catdesc})
			kitjson.update({'dist': round(dist, 1)})
			reviews = Reviews.objects.filter(kit_id=i.id)
			if reviews:
				avgrating = round(reviews.aggregate(Avg('ratings'))['ratings__avg'], 1)
				kitjson.update({'avgrating': avgrating})
			else :
				kitjson.update({'avgrating': None})
			kit_object.append(kitjson)
	kit_object.sort(key=lambda x: x['dist'])
	context = {
 		'kit_object': kit_object,
	}
	return Response(context)


@api_view(['POST'])
def getKitchen(request):
	longitude = request.data['lon']
	latitude = request.data['lat']
	user_location = Point(float(longitude), float(latitude), srid=4326)
	if 'kitId' in request.data.keys():
		kitId = request.data['kitId']
		kitchen = Kitchens.objects.get(id=kitId)
		dist = user_location.distance(kitchen.location) * 100
		kitjson = KitchensSerializer(kitchen).data
		catdesc = ""
		categories = Categories.objects.filter(kit_id=kitchen.id)
		for cat in categories:
			catdesc = catdesc + cat.category + ", "
		kitjson['catdesc'] = catdesc
		kitjson['dist'] = round(dist, 1)
		reviews = Reviews.objects.filter(kit_id=kitchen.id)
		if reviews:
			avgrating = round(reviews.aggregate(Avg('ratings'))['ratings__avg'], 1)
			kitjson['avgrating'] = avgrating
		else :
			kitjson['avgrating'] = None
		fav = FavouriteKitchens.objects.filter(customer_id=request.user.id, kitchen_id=kitchen.id).first()
		if fav:
			kitjson.update({'favourite': True})
		else:
			kitjson.update({'favourite': False})
		context = {
			'kit_object': kitjson,
		}
	else :
		kitchens = Kitchens.objects.filter(approved=True)
		kit_object = []
		for i in kitchens:
			dist = user_location.distance(i.location) * 100
			kitjson = KitchensSerializer(i).data
			catdesc = ""
			categories = Categories.objects.filter(kit_id=i.id)
			for cat in categories:
				catdesc = catdesc + cat.category + ", "
			kitjson.update({'catdesc': catdesc})
			kitjson.update({'dist': round(dist, 1)})
			reviews = Reviews.objects.filter(kit_id=i.id)
			if reviews:
				avgrating = round(reviews.aggregate(Avg('ratings'))['ratings__avg'], 1)
				kitjson.update({'avgrating': avgrating})
			else :
				kitjson.update({'avgrating': None})
			kit_object.append(kitjson)
		context = {
			'kit_object': kit_object,
		}
	return Response(context)


@api_view(['POST'])
def menu(request):
	kitId = request.data['kitId']
	menu = Menus.objects.filter(kit_id=kitId)

	items = []
	for i in menu:
		menuItemJson =  MenuSerializer(i).data
		discRate = int(i.item.price) - int(int(i.offer)/100 * int(i.item.price))
		menuItemJson.update({'discountrate': discRate})
		subitems = SubItems.objects.filter(item_id=i.item_id)
		tempsubitems = []
		for sub in subitems:
			subItemJson = SubItemsSerializer(sub).data
			discRateOfSubItem = int(sub.price) - (int(i.offer)/100 * int(sub.price))
			subItemJson.update({'discountrate': discRateOfSubItem})
			tempsubitems.append(subItemJson)
		menuItemJson.update({'subitems': tempsubitems})
		items.append(menuItemJson)

	reviews = Reviews.objects.filter(kit_id=kitId)
	reviewjson = ReviewSerializer(reviews, many=True).data

	categories = Categories.objects.filter(kit_id=kitId)
	categoryjson = CategorySerializer(categories, many=True).data

	context = {
		'categories': categoryjson,
		'menuitems': items,
		'reviews': reviewjson,
	}
	return Response(context)


@api_view(['POST'])
def cart(request):
	kit = request.data['kitId']
	cartItems = request.data['cartItems']
	currentDate = getCurrentDate()
	addresses = Addresses.objects.filter(user_id=request.user.id)
	addjson = AddressSerializer(addresses, many=True).data

	kitchen = Kitchens.objects.filter(id=kit)[0]
	kitjson = KitchensSerializer(kitchen).data

	kitCoupons = UserDiscountCoupons.objects.filter(Q(user_id=request.user.id) | Q(user=None), kit=kitchen, redeemed=False, validTill__gte=currentDate)
	couponsjson = CouponsSerializer(kitCoupons, many=True).data

	menu = Menus.objects.filter(kit_id=kit)
	items = []
	subtotal = 0
	discount = 0
	kitDiscount = 0
	total = 0
	for i in menu:
		itemid = str(i.item_id)
		temp = {}
		for j in cartItems:
			if (itemid == str(j['itemId'])):
				quant = j['qty']
				if quant != 0:
					item = Items.objects.filter(id=i.item_id)[0]
					temp.update({'image': item.image.url})
					temp.update({'name': item.itemName})
					temp.update({'desc': item.itemDesc})
					temp.update({'price': item.price})
					temp.update({'type': item.itemType})
					temp.update({'qty': quant})
					temp.update({'offer': int(i.offer)})
					temp.update({'id': item.id})
					temp.update({'minOrder': i.minOrder})
					items.append(temp)
			elif (itemid + "-" in str(j['itemId'])):
				subitems = SubItems.objects.filter(item_id=i.item_id)
				for sub in subitems:
					temp = {}
					x = itemid + "-" + str(sub.id)
					if x == str(j['itemId']):
						quant = j['qty']
						if quant != 0:
							item = Items.objects.filter(id=i.item_id)[0]
							temp.update({'image': item.image.url})
							temp.update({'name': item.itemName + "  ( " + sub.name + " )"})
							temp.update({'desc': item.itemDesc})
							temp.update({'price': sub.price})
							temp.update({'type': item.itemType})
							temp.update({'qty': quant})
							temp.update({'offer': int(i.offer)})
							temp.update({'id': str(item.id)+"-"+str(sub.id)})
							temp.update({'minOrder': i.minOrder})
							items.append(temp)	
		
	context = {
		'items': items,
		'kitchen': kitjson,
		'addresses': addjson,
		'kitCoupons': couponsjson,
	}
	return Response(context)


@api_view(['POST'])
def checkUser(request):
	context = {}
	phone = request.data['phone']
	user = User.objects.filter(phone=phone)
	if user.count() != 0:
		context['resp'] = "UserVerified"
	else:
		context['resp'] = "userNotReg"
	return Response(context)


@api_view(['POST'])
def login(request):
	context = {}
	phone = request.data['phone']
	user = User.objects.filter(phone=phone)
	if user.count() != 0:
		if user[0].is_active:
			update_last_login(None, user[0])
			token = Token.objects.get(user=user[0])
			context['token'] = token.key
		else:
			raise APIException("Your Account is Disabled")
	else:
		raise APIException("Invalid Login")
	return Response(context)


@api_view(['POST'])
def register(request):
	context = {}
	form = UserSerializer(data=request.data)
	if form.is_valid():
		user = form.save()
		user.is_customer = True
		update_last_login(None, user)
		user.save()
		phone = request.data['phone']
		user = User.objects.filter(phone=phone)
		if user.count() != 0:
			token = Token.objects.get(user=user[0])
			context['token'] = token.key
		else:
			raise APIException("User could not be registsred successfully. Please try again.")
	else:
		context = form.errors
	return Response(context)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def updateProfile(request):
	context = {}
	valid = True

	phone = request.data['phone']
	user = User.objects.filter(phone=phone)
	if user.count() != 0 and phone != request.user.phone:
		context['phone'] = "Phone no already exists"
		valid = False

	email = request.data['email']
	if checkEmail(email):
		user = User.objects.filter(email=email)
		if user.count() != 0 and email != request.user.email:
			context['email'] = "Email already exists"
			valid = False
	else:
		context['email'] = "Entered Email is Invalid"
		valid = False
		
	if valid:
		User.objects.filter(id=request.user.id).update(email=email, phone=phone)
		context['response'] = "Details Updated Successfully"
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
def getAddresses(request):
	addresses = Addresses.objects.filter(user_id=request.user.id)
	addjson = AddressSerializer(addresses, many=True).data
	context = {
		'addresses': addjson,
	}
	return Response(context)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def saveAddress(request):
	context = {}
	if request.data['action'] == "add":
		addform = AddressSerializer(data=request.data)
		if addform.is_valid():
			lon = request.data['longitude']
			lat = request.data['latitude']
			addinstance = addform.save(user=request.user)
			addinstance.location = Point(lon, lat, srid=4326)
			addinstance.save()
			context['response'] = "Address Added Successfully"
		else:
			context = addform.errors
	elif request.data['action'] == "update":
		addid = request.data['addid']
		lon = request.data['longitude']
		lat = request.data['latitude']
		Addresses.objects.filter(id=addid).update(place=request.data['place'],latitude=lat,longitude=lon,location=Point(lon, lat, srid=4326),address=request.data['address'],floorNo=request.data['floorNo'])
		context['response'] = "Address Updated Successfully"
	elif request.data['action'] == "delete":
		addid = request.data['addid']
		Addresses.objects.filter(id=addid).delete()
		context['response'] = "Address Deleted Successfully"
	return Response(context)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def favouriteKitchens(request):
	longitude = request.data['lon']
	latitude = request.data['lat']
	user_location = Point(float(longitude), float(latitude), srid=4326)
	kitchen_ids = FavouriteKitchens.objects.filter(customer=request.user)
	kit_object = []
	for i in kitchen_ids:
		dist = user_location.distance(i.kitchen.location) * 100
		kitjson = KitchensSerializer(i.kitchen).data
		catdesc = ""
		categories = Categories.objects.filter(kit_id=i.kitchen.id)
		for cat in categories:
			catdesc = catdesc + cat.category + ", "
		kitjson.update({'catdesc': catdesc})
		kitjson.update({'dist': round(dist, 1)})
		reviews = Reviews.objects.filter(kit_id=i.kitchen.id)
		if reviews:
			avgrating = round(reviews.aggregate(Avg('ratings'))['ratings__avg'], 1)
			kitjson.update({'avgrating': avgrating})
		else :
			kitjson.update({'avgrating': None})
		kit_object.append(kitjson)
	context = {
		'kit_object': kit_object,
	}
	return Response(context)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_to_favourite(request):
	kitId = request.data['kitId']
	fav = FavouriteKitchens.objects.filter(customer_id=request.user.id, kitchen_id=kitId).first()
	if fav:
		FavouriteKitchens.objects.filter(id=fav.id).delete()
		context = {
			'response': "Deleted",
		}
	else:
		print(kitId, request.user)
		FavouriteKitchens.objects.create(kitchen_id=kitId, customer=request.user)
		context = {
			'response': "Added",
		}
	return Response(context)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def orders(request):
	if request.data:
		orders = Order.objects.filter(Q(status="Placed") | Q(status="Ready") | Q(status="Preparing") | Q(status="Dispatched") | Q(status="Waiting") | Q(status="Payment"), customer_id=request.user.id).order_by("-created_at")
	else:	
		orders = Order.objects.filter(customer_id=request.user.id).order_by("-created_at")
	orders_object = []
	for i in orders:
		ordersjson = OrderSerializer(i).data
		ordersjson.update({'kitchen': KitchensSerializer(i.kitchen).data})
		ordersjson.update({'delivery_addr': AddressSerializer(i.delivery_addr).data})
		orders_object.append(ordersjson)
	context = {
		'orders': orders_object,
	}
	return Response(context)


@api_view(['POST'])
def fetchOrder(request):
	context = {}
	orderid = request.data['orderid']
	order = Order.objects.filter(id=orderid)[0]
	ordersjson = OrderSerializer(order).data
	ordersjson.update({'kitchen': KitchensSerializer(order.kitchen).data})
	ordersjson.update({'delivery_addr': AddressSerializer(order.delivery_addr).data})
	context = {
		'order': ordersjson,
	}
	return Response(context)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getAndAddReviews(request):
	context = {}
	kitId = request.data['kitId']
	userid = request.user.id
	reviews = Reviews.objects.filter(user_id=userid, kit_id=kitId)
	if request.data['action'] == "get":
		if reviews.count() == 0:
			reviewsjson = {"kit" : kitId}
		else:
			reviewsjson = ReviewSerializer(reviews[0]).data
		context['reviews'] = reviewsjson
	else :
		if reviews.count() == 0:
			Reviews.objects.create(ratings=request.data['rating'], reviews=request.data['comment'], kit_id=kitId, user_id=userid)
		else:
			Reviews.objects.filter(user_id=userid, kit_id=kitId).update(ratings=request.data['rating'], reviews=request.data['comment'])
		context['response'] = "Reviews updated Successfully"
	return Response(context)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def placeOrder(request):
	context = {}
	currentDate = getCurrentDate()
	subTotal = request.data['subTotal']
	total = request.data['total']
	coupDiscount = request.data['coupDiscount']
	kitDiscount = request.data['kitDiscount']
	couponId = request.data['couponId']
	mode = request.data['mode']
	deliveryCharge = request.data['deliveryCharge']
	cartItems = request.data['cartItems']
	add = request.data['add']
	msg = request.data['msg']
	scheduledDate = request.data['scheduledDate']
	kit = request.data['kit']

	itemswithquantity = ""
	for i in cartItems:
		itemswithquantity = itemswithquantity + \
			i.get('name') + "  X  " + str(i.get('qty')) + ", "

	res = calc_distance(kit, add)
	dist = res['distance']

	cust = request.user

	var = dateparse.parse_datetime(scheduledDate)
	scheduledDate = currentDate.replace(var.year, var.month, var.day, var.hour, var.minute)

	activeOrders = check_active_orders(request.user.id)
	if activeOrders < 2:
		order = Order.objects.create(sub_total=subTotal, total_amount=total, coup_discount=coupDiscount, kit_discount=kitDiscount, coupon_id=couponId, balance=total, mode=mode, delivery_charge=deliveryCharge, itemswithquantity=itemswithquantity, delivery_addr_id=add, dist_from_kit=dist, message=msg, scheduled_order=scheduledDate, customer=cust, kitchen_id=kit, created_at=currentDate)
		context = {
			'orderid': order.id,
			'response': "Order placed Successfully"
		}
	else:
		context['response'] = "Order can't be placed, Maximum 2 active orders are allowed"

	return Response(context)


def calc_distance(kitchenid, addid):
	deliveryaddress = Addresses.objects.filter(id=addid)[0]
	kitchen = Kitchens.objects.filter(id=kitchenid)[0]
	distance = deliveryaddress.location.distance(kitchen.location) * 100
	context = {
		"distance": round(distance,1),
		"deliveryadd": deliveryaddress.address + ", Floor No.- " + deliveryaddress.floorNo,
	}
	return context


def check_active_orders(custid):
    return Order.objects.filter(Q(status="Placed") | Q(status="Ready") | Q(status="Preparing") | Q(status="Dispatched") | Q(status="Waiting") | Q(status="Payment"), customer_id=custid).count()


@api_view(['POST'])
def cancelOrder(request):
	context = {}
	currentDate = getCurrentDate()
	orderid = request.data['orderid']
	action = request.data['action']
	order = Order.objects.filter(id=orderid)
	message = request.data['message']
	if len(message) == 0:
		message = "Customer Cancelled the Order"
	status = "Cancelled"
	
	if action == "cancelFromKitSide":
		msgtocust = "Kitchen Not Responding"
		if order[0].coupon_id != None and order[0].coupon.user != None:
			update_coupon(order[0].coupon_id, False)
		res = order.update(status=status, completed_at=currentDate, msgtocust=msgtocust)
	elif action == "cancelFromCustSide":
		msg = message
		if order[0].coupon_id != None and order[0].coupon.user != None:
			update_coupon(order[0].coupon_id, False)
		if order[0].amount_paid > 0:
			refundStatus = "Under Process"
			issue = message
			comments = ""
			subject = "Refund"
			raise_complaint_refund(order[0].kitchen, order[0], order[0].customer, comments, issue, refundStatus, order[0].customer.phone, subject)
		res = order.update(status=status, completed_at=currentDate, message=msg)

	if res == 1:
		context['response'] = "Order cancelled Successfully"
	else:
		context['response'] = "Problem Occured. Try again."
	return Response(context)


@api_view(['POST'])
def orderHelp(request):
	context = {}
	orderid = request.data['orderid']
	order = Order.objects.filter(id=orderid)
	paytmNo = request.data['phone']
	subject = request.data['subject']
	issue = request.data['query']
	status = "Under Process"
	comments = ""
	raise_complaint_refund(order[0].kitchen, order[0], order[0].customer, comments, issue, status, paytmNo, subject)
	context['response'] = "Request registered Successfully"
	return Response(context)


def update_coupon(couponId, redeemed):
	UserDiscountCoupons.objects.filter(id=couponId).update(redeemed=redeemed)


def raise_complaint_refund(kitchen, order, cust, comments, issue, status, paytmNo, subject):
	currentDate = getCurrentDate()
	ComplaintsAndRefunds.objects.create(kit=kitchen, order=order, user=cust, comments=comments, issue=issue, status=status, paytmNo=paytmNo, request_date=currentDate, subject=subject)