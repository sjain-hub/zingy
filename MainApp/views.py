from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .forms import CustomerSignUpForm, UserAddressesForm, CustomerUserProfileForm
from django.contrib.auth.decorators import login_required
from .models import User, Addresses, Order, FavouriteKitchens, Queries
from kitchen.models import Kitchens, Categories, Menus, Items, SubItems, Reviews, ComplaintsAndRefunds, UserDiscountCoupons
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.http import HttpResponse, JsonResponse
from django.db.models import Avg, Q
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
import http.client
from . import FCMManager as fcm


tokens = ["dDNsYEH3T6-Swao2uFmft5:APA91bFBoLeTBLy5q0B5d-V3lX9Ye-bNn2M3LCh7_Ia2vvBd6CKDK-PkfrLFQ6Qt7l5A5__otYBH1uBXfuGK3x1zDHyB8mQRmYj0RQSv8gz7SKiAPpoBXqPuF6-ow1L8vDlsSHphcc-b", "dDSUrXzROcFD5ICjWZbC48:APA91bEaGRE9tqViTnCclZ_-Crro7HsqMi6StB4hOClckBV8noDVVwlDtaugUL71uwH61e5IxCFhGUS25gqXZL7zxHT5LM37E53IPwpzsAvpwKmZF2a1kK1ti3Mns4BhbHwP8PDo1wcC"]

def sendNotification():
	fcm.sendPush("Hi", "This is my next msg", tokens)


def getServiceWorker(request):
	return render(request, 'firebase-messaging-sw.js', content_type="application/x-javascript")


def getCurrentDate():
	return datetime.now()


def index(request):
	if request.user.is_authenticated:
		if request.user.is_kitchen:
			return redirect("kitchenHomePage")
	kit_object = Kitchens.objects.filter(approved=True)
	context = {
		'kit_object': kit_object
	}
	return render(request, 'index.html', context)


def test(request):
	return render(request, 'test.html')


def Logout(request):
	logout(request)
	return redirect("index")
	# if request.user.is_kitchen:
	# 	logout(request)
	# 	return redirect("kitchenLogin")
	# else:
	# 	logout(request)
	# 	return redirect("index")


def nearbyKitchens(request):
	if request.user.is_authenticated:
		if request.user.is_kitchen:
			return redirect("kitchenHomePage")
	longitude = request.COOKIES['lon']
	latitude = request.COOKIES['lat']
	user_location = Point(float(longitude), float(latitude), srid=4326)
	# kit_object = Kitchens.objects.filter(location__dwithin=(user_location, 0.02), approved=True).annotate(
	# 	distance=Distance("location", user_location)).order_by("distance")
	query 	= request.GET.get('search')
	if query:
		kitchens=Kitchens.objects.filter(Q(kitName__icontains=query))
		kit_object = []
		for i in kitchens:
			dist = user_location.distance(i.location) * 100
			temp = []
			temp.append(i)
			catdesc = ""
			categories = Categories.objects.filter(kit_id=i.id)
			for cat in categories:
				catdesc = catdesc + cat.category + ", "
			temp.append(catdesc)
			temp.append(round(dist,1))
			reviews = Reviews.objects.filter(kit_id=i.id)
			avgrating = reviews.aggregate(Avg('ratings'))
			temp.append(avgrating)
			kit_object.append(temp)
	else:
		kitchens = Kitchens.objects.filter(approved=True)
		kit_object = []
		for i in kitchens:
			dist = user_location.distance(i.location) * 100
			if dist <= i.deliveryRadius:
				temp = []
				temp.append(i)
				catdesc = ""
				categories = Categories.objects.filter(kit_id=i.id)
				for cat in categories:
					catdesc = catdesc + cat.category + ", "
				temp.append(catdesc)
				temp.append(round(dist,1))
				reviews = Reviews.objects.filter(kit_id=i.id)
				avgrating = reviews.aggregate(Avg('ratings'))
				temp.append(avgrating)
				kit_object.append(temp)
	cartitemcount = countCartItems(request)
	context = {
 		'kit_object': kit_object,
		'cartitemcount': cartitemcount,
	}
	return render(request, 'kitchens.html', context)


@login_required(login_url='/login/')
def favouriteKitchens(request):
	if request.user.is_kitchen:
		return redirect("kitchenHomePage")
	longitude = request.COOKIES['lon']
	latitude = request.COOKIES['lat']
	user_location = Point(float(longitude), float(latitude), srid=4326)
	kitchen_ids = FavouriteKitchens.objects.filter(customer=request.user)
	kit_object = []
	for i in kitchen_ids:
		dist = user_location.distance(i.kitchen.location) * 100
		temp = []
		temp.append(i.kitchen)
		catdesc = ""
		categories = Categories.objects.filter(kit_id=i.kitchen.id)
		for cat in categories:
			catdesc = catdesc + cat.category + ", "
		temp.append(catdesc)
		temp.append(round(dist,1))
		reviews = Reviews.objects.filter(kit_id=i.kitchen.id)
		avgrating = reviews.aggregate(Avg('ratings'))
		temp.append(avgrating)
		kit_object.append(temp)
	cartitemcount = countCartItems(request)
	context = {
 		'kit_object': kit_object,
		'cartitemcount': cartitemcount,
	}
	return render(request, 'favouriteKitchens.html', context)


def update_variable(value):
    data = value
    return data


def add_to_favourite(request, pk=None):
	fav = FavouriteKitchens.objects.filter(customer_id=request.user.id, kitchen_id=pk).first()
	if fav == None:
		FavouriteKitchens.objects.create(kitchen_id=pk, customer=request.user)
		return JsonResponse({"success_message": 'Marked as Favourite.'}, status=200)
	else:
		FavouriteKitchens.objects.filter(id=fav.id).delete()
		return JsonResponse({"success_message": 'Deleted as Favourite.'}, status=200)


def Menu(request, pk=None):
	if request.user.is_authenticated:
		if request.user.is_kitchen:
			return redirect("kitchenHomePage")
	fav = FavouriteKitchens.objects.filter(customer_id=request.user.id, kitchen_id=pk).first()
	if fav == None:
		favourite = False
	else:
		favourite = True
	categories = Categories.objects.filter(kit_id=pk)
	menu = Menus.objects.filter(kit_id=pk)
	kitchen = Kitchens.objects.filter(id=pk)

	cartitemcount = countCartItems(request)
	
	vegSelected = False
	items = []
	item = ''
	for i in menu:
		if 'veg' in request.COOKIES:
			if request.COOKIES['veg'] == 'true':
				vegSelected = True
				item = Items.objects.filter(id=i.item_id, itemType='veg')
			else:
				item = Items.objects.filter(id=i.item_id)
		else:
			item = Items.objects.filter(id=i.item_id)
		subitems = SubItems.objects.filter(item_id=i.item_id)
		for content in item:
			menuitemid = str(content.id)
			temp = []
			totalquant = 0
			temp.append(content.itemName)
			temp.append(content.category)
			temp.append(content.itemType)
			temp.append(content.price)
			temp.append(content.image)
			temp.append(content.itemDesc)
			temp.append(int(i.offer))
			temp.append(content.id)
			temp.append(i.out_of_stock)
			temp.append(i.minOrder)

			subtemp = []
			for sub in subitems:
				temp1 = []
				x = menuitemid + "-" + str(sub.id)
				temp1.append(sub.id)
				temp1.append(sub.name)
				temp1.append(sub.price)
				if x in request.COOKIES.keys():
					if request.COOKIES[x] != '0':
						temp1.append(request.COOKIES[x])
						totalquant = totalquant + int(request.COOKIES[x])
					else:
						temp1.append(0)
				else:
					temp1.append(0)
				discRateOfSubItem = int(sub.price) - (int(i.offer)/100 * int(sub.price))
				temp1.append(discRateOfSubItem)
				subtemp.append(temp1)
			temp.append(subtemp)

			if menuitemid in request.COOKIES.keys():
				if request.COOKIES[menuitemid] != '0':
					temp.append(request.COOKIES[menuitemid])
				else:
					temp.append(0)
			else:
				temp.append(totalquant)
			temp.append(content.condition)
			discRate = int(content.price) - int(int(i.offer)/100 * int(content.price))
			temp.append(discRate)
			items.append(temp)

	reviews = Reviews.objects.filter(kit_id=pk)
	avgrating = reviews.aggregate(Avg('ratings'))

	context = {
		'categories': categories,
		'menuitems': items,
		'kitchen': kitchen[0],
		'reviews': reviews,
		'avgrating': avgrating,
		'cartitemcount': cartitemcount,
		'favourite': favourite,
		'vegSelected': vegSelected,
	}
	return render(request, 'menu.html', context)


def countCartItems(request):
	cartitemcount = 0
	cart = request.COOKIES.items()
	for x in cart:
		if x[0].isdigit() or x[0].split("-")[0].isdigit():
			if x[1] != '0':
				cartitemcount = cartitemcount + int(x[1])
	return cartitemcount


def Cart(request):
	if request.user.is_authenticated:
		if request.user.is_kitchen:
			return redirect("kitchenHomePage")
	currentDate = getCurrentDate()
	cartitemcount = countCartItems(request)
	addform = UserAddressesForm(request.POST or None)
	
	# for adding the addresses
	if request.POST:
		if addform.is_valid():
			lon = addform.cleaned_data['longitude']
			lat = addform.cleaned_data['latitude']

			addinstance = addform.save(commit=False)
			addinstance.location = Point(lon, lat, srid=4326)
			addinstance.user = request.user
			addinstance.save()

	if 'kit' in request.COOKIES.keys():
		addresses = Addresses.objects.filter(user_id=request.user.id)
		kitchen = Kitchens.objects.filter(id=request.COOKIES['kit'])[0]
		kitCoupons = UserDiscountCoupons.objects.filter(Q(user_id=request.user.id) | Q(user=None), kit=kitchen, redeemed=False, validTill__gte=currentDate)
		menu = Menus.objects.filter(kit_id=request.COOKIES['kit'])
		items = []
		subtotal = 0
		discount = 0
		kitDiscount = 0
		total = 0
		for i in menu:
			itemid = str(i.item_id)
			temp = []
			if itemid in request.COOKIES.keys():
				quant = request.COOKIES[itemid]
				if quant != '0':
					item = Items.objects.filter(id=i.item_id)
					temp.append(item[0].image)
					temp.append(item[0].itemName)
					temp.append(item[0].itemDesc)
					temp.append(item[0].price)
					temp.append(quant)
					if int(i.offer) > 0:
						disc = int(i.offer)/100 * int(item[0].price)
						kitDiscount = kitDiscount + int(disc * int(quant))
					total_price = item[0].price * int(quant)	
					subtotal = subtotal + total_price
					temp.append(total_price)
					temp.append(item[0].id)
					temp.append(i.minOrder)
					items.append(temp)
			elif any(itemid+"-" in s for s in request.COOKIES.keys()):
				subitems = SubItems.objects.filter(item_id=i.item_id)
				for sub in subitems:
					temp = []
					x = itemid + "-" + str(sub.id)
					if x in request.COOKIES.keys():
						quant = request.COOKIES[x]
						if quant != '0':
							item = Items.objects.filter(id=i.item_id)
							temp.append(item[0].image)
							temp.append(item[0].itemName + "  ( " + sub.name + " )")
							temp.append(item[0].itemDesc)
							temp.append(sub.price)
							temp.append(quant)
							if int(i.offer) > 0:
								disc = int(i.offer)/100 * int(sub.price)
								kitDiscount = kitDiscount + int(disc * int(quant))
							total_price = sub.price * int(quant)	
							subtotal = subtotal + total_price
							temp.append(total_price)
							temp.append(str(item[0].id)+"-"+str(sub.id))
							temp.append(i.minOrder)
							items.append(temp)

		total = subtotal - kitDiscount
		
		
		advanceOrder = False
		if "advanceOrder" in request.COOKIES.keys():
			if request.COOKIES['advanceOrder'] == "true":
				advanceOrder = True

		coupon = ''
		if 'couponId' in request.COOKIES.keys():
			coupon = UserDiscountCoupons.objects.filter(id=request.COOKIES['couponId'])[0]
			discount = int(coupon.discount/100 * total)
			if discount > coupon.maxDiscount:
				discount = coupon.maxDiscount
			total = total - discount
		
		modeSelected = kitchen.mode
		if "modeSelected" in request.COOKIES.keys():
			modeSelected = request.COOKIES['modeSelected']
			if modeSelected == "Delivery":
				total = total + kitchen.deliveryCharge
		else:
			if modeSelected == "Delivery":
				total = total + kitchen.deliveryCharge

		mindate = getCurrentDate().isoformat()
		maxdate = (getCurrentDate().replace(hour=23, minute=59) + timedelta(days=2)).isoformat()[:16]

		if request.method=="GET":
			if 'websocket' in request.GET.keys():
				items1 = []
				for item in items:
					temp = {}
					temp['itemName'] = item[1]
					temp['quantity'] = item[4]
					items1.append(temp)
				context = {
					'items': items1,
				}
				return JsonResponse(context, status=200)
			
		context = {
			'items': items,
			'subtotal': subtotal,
			'kitchen': kitchen,
			'total': total,
			'cartitemcount': cartitemcount,
			'addressform': addform,
			'addresses': addresses,
			'modeSelected': modeSelected,
			'advanceOrder': advanceOrder,
			'mindate': mindate,
			'maxdate': maxdate,
			'kitCoupons': kitCoupons,
			'coupDiscount': discount,
			'kitDiscount': kitDiscount,
			'selectedCoupon': coupon,
		}
		return render(request, 'cart.html', context)
	else:
		context = {
			'cartitemcount': cartitemcount,
		}
		return render(request, 'cart.html', context)


def Login(request):
	if request.method=="POST":
		username = request.POST['username']
		password = request.POST['password']
		user     = authenticate(username=username,password=password)
		if user is not None and not user.is_kitchen:
			if user.is_active:
				login(request,user)
				return JsonResponse({"success_message": 'Login Successful.'}, status=200)
			else:
				return JsonResponse({"error_message": 'Your Account is Disabled.'}, status=200)
		else:
			return JsonResponse({"error_message": 'Invalid Login'}, status=200)
	return render(request, 'login.html')


def Register(request):
	if request.method == "POST":
		form = CustomerSignUpForm(request.POST or None)
		if form.is_valid():
			user = form.save(commit=False)
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user.is_customer = True
			user.set_password(password)
			user.save()
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					return JsonResponse({"success_message": 'Login Successful.'}, status=200)
		else:
			context = {
				'form': form
			}
			return render(request, 'register.html', context)
	else:
		form = CustomerSignUpForm()
		context = {
			'form': form
		}
		return render(request, 'register.html', context)

@login_required(login_url='/login/')
def updateProfile(request):
	if request.user.is_kitchen:
		return redirect("kitchenHomePage")
	form = CustomerUserProfileForm(request.POST or None, instance=request.user)
	if request.POST:
		if form.is_valid():
			if 'submit' in request.POST.keys():
				type = request.POST['submit']
				if type == "username":
					print("username")
					User.objects.filter(id=request.user.id).update(username=form.cleaned_data['username'])
				elif type == "fname":
					print("fname")
					User.objects.filter(id=request.user.id).update(first_name=form.cleaned_data['first_name'])
				elif type == "lname":
					print("lname")
					User.objects.filter(id=request.user.id).update(last_name=form.cleaned_data['last_name'])
				elif type == "email":
					print("email")
					User.objects.filter(id=request.user.id).update(email=form.cleaned_data['email'])
				elif type == "phone":
					print("phone")
					User.objects.filter(id=request.user.id).update(phone=form.cleaned_data['phone'])
				elif type == "pass":
					user = form.save(commit=False)
					username = form.cleaned_data['username']
					password = form.cleaned_data['password']
					rpassword = request.POST['rpassword']
					if password != rpassword:
						context = {
							'form': form,
							'error_message': "Passwords didn't Match"
						}
						return render(request, 'userProfile.html', context)
					user.set_password(password)
					user.save()
					user = authenticate(username=username, password=password)
					if user is not None:
						if user.is_active:
							login(request, user)
	context = {
			'form': form
		}
	return render(request, 'userProfile.html', context)


# def Checkout(request):
# 	addid = request.POST['address']
# 	deladdress = Addresses.objects.filter(id=addid)
# 	kitid = request.COOKIES['kit']
# 	kitchen = Kitchens.objects.filter(id=kitid)

# 	distance=deladdress[0].location.distance(kitchen[0].location) * 100
# 	if distance > 3:
# 		return JsonResponse({"error_message": 'This Kitchen does not deliver to this location.'}, status=200)
# 	pass


@login_required(login_url='/login/')
def orders(request):
	if request.user.is_kitchen:
		return redirect("kitchenHomePage")
	cartitemcount = countCartItems(request)
	orders = Order.objects.filter(customer_id=request.user.id).order_by("-created_at")

	for i in orders:
		i.itemswithquantity = i.itemswithquantity.split(",")
	
	context = {
		'cartitemcount': cartitemcount,
		'orders': orders,
	}
	return render(request, 'orders.html', context)


def addReview(request):
	kitid = request.POST['kitid']
	userid = request.user.id
	reviews = Reviews.objects.filter(user_id=userid, kit_id=kitid)
	if 'comment' in request.POST.keys():
		if reviews.count() == 0:
			Reviews.objects.create(ratings=request.POST['rating'], reviews=request.POST['comment'], kit_id=kitid, user_id=userid)
		else:
			Reviews.objects.filter(user_id=userid, kit_id=kitid).update(ratings=request.POST['rating'], reviews=request.POST['comment'])
		return JsonResponse({"success_message": 'Response Added Successfully.'}, status=200)
	else:
		if reviews.count() == 0:
			return JsonResponse({"ratings": "", "reviews": ""}, status=200)
		else:
			return JsonResponse({"ratings": reviews[0].ratings, "reviews": reviews[0].reviews}, status=200)


def sendQueries(request):
	currentDate = datetime.now()
	order = Order.objects.filter(id=request.POST['orderId'])[0]
	paytmNo = request.POST['phone']
	subject = request.POST['subject']
	query = request.POST['query']
	status = "Under Process"
	ComplaintsAndRefunds.objects.create(kit=order.kitchen, order=order, user=order.customer, subject=subject, issue=query, status=status, paytmNo=paytmNo, request_date=currentDate)
	return JsonResponse({"success_message": 'Query Submitted Successfully.'}, status=200)


@login_required(login_url='/login/')
def orderStatus(request, pk=None):
	if request.user.is_kitchen:
		return redirect("kitchenHomePage")
	context = {
		'order': Order.objects.filter(id=pk)[0],
	}
	return render(request, 'orderStatus.html', context)


def contactUs(request):
	submitted = False
	if request.POST:
		Queries.objects.create(name=request.POST['name'], email=request.POST['email'], phone=request.POST['phone'], subject=request.POST['subject'], message=request.POST['message'], reqDate=getCurrentDate())
		submitted = True
	context = {
		'address': settings.ADDRESS,
		'phone': settings.PHONE,
		'email': settings.EMAIL,
		'lat': settings.LATITUDE,
		'lon': settings.LONGITUDE,
		'formSubmitted': submitted,
	}
	return render(request, 'contact.html', context)


def updates(request):
	return render(request, 'updates.html')
