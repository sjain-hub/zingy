from rest_framework.response import Response
from django.contrib.auth import login, logout
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from kitchen.models import Kitchens, Reviews, Categories, Menus, Items, SubItems, Reviews, UserDiscountCoupons
from MainApp.models import FavouriteKitchens, Addresses, User
from .serializers import KitchensSerializer, CategorySerializer, ReviewSerializer, AddressSerializer, CouponsSerializer, UserSerializer
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


regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'


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
	longitude = request.data['lon']
	latitude = request.data['lat']
	user_location = Point(float(longitude), float(latitude), srid=4326)
	kitchens = Kitchens.objects.filter(approved=True)
	kit_object = []
	for i in kitchens:
		dist = user_location.distance(i.location) * 100
		if dist <= i.visibilityRadius:
			kitjson = KitchensSerializer(i).data
			catdesc = ""
			categories = Categories.objects.filter(kit_id=i.id)
			for cat in categories:
				catdesc = catdesc + cat.category + ", "
			kitjson.update({'catdesc': catdesc})
			kitjson.update({'dist': round(dist, 1)})
			reviews = Reviews.objects.filter(kit_id=i.id)
			avgrating = reviews.aggregate(Avg('ratings'))
			kitjson.update(avgrating)
			kit_object.append(kitjson)
	context = {
 		'kit_object': kit_object,
	}
	return Response(context)


@api_view(['POST'])
def menu(request):
	kitId = request.data['kitId']
	categories = Categories.objects.filter(kit_id=kitId)
	categoryjson = CategorySerializer(categories, many=True).data
	menu = Menus.objects.filter(kit_id=kitId)

	items = []
	item = ''
	for i in menu:
		item = Items.objects.filter(id=i.item_id)
		subitems = SubItems.objects.filter(item_id=i.item_id)
		for content in item:
			menuitemid = str(content.id)
			temp = {}
			totalquant = 0
			temp.update({'name': content.itemName})
			temp.update({'category': content.category.category})
			temp.update({'type': content.itemType})
			temp.update({'price': content.price})
			temp.update({'image': content.image.url})
			temp.update({'desc': content.itemDesc})
			temp.update({'offer': int(i.offer)})
			temp.update({'id': content.id})
			temp.update({'out_of_stock': i.out_of_stock})
			temp.update({'minOrder': i.minOrder})

			subtemp = []
			for sub in subitems:
				temp1 = {}
				x = menuitemid + "-" + str(sub.id)
				temp1.update({'id': sub.id})
				temp1.update({'name': sub.name})
				temp1.update({'price': sub.price})
				discRateOfSubItem = int(sub.price) - (int(i.offer)/100 * int(sub.price))
				temp1.update({'discountrate': discRateOfSubItem})
				subtemp.append(temp1)
			temp.update({'subitems': subtemp})

			temp.update({'condition': content.condition})
			discRate = int(content.price) - int(int(i.offer)/100 * int(content.price))
			temp.update({'discountrate': discRate})
			items.append(temp)

	reviews = Reviews.objects.filter(kit_id=kitId)
	reviewjson = ReviewSerializer(reviews, many=True).data

	context = {
		'categories': categoryjson,
		'menuitems': items,
		'reviews': reviewjson,
		# 'favourite': favourite,
	}
	return Response(context)


@api_view(['POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
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
def updateProfile(request):
	context = {}
	phone = request.data['phone']
	email = request.data['email']
	if checkEmail(email):
		User.objects.filter(id=request.user.id).update(email=email, phone=phone)
		context['response'] = "Details Updated Successfully"
	else:
		raise APIException("Enter Valid Email")
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
