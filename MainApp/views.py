from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .forms import CustomerSignUpForm, UserAddressesForm, CustomerUserProfileForm
from django.contrib.auth.decorators import login_required
from .models import User, Addresses, Order, FavouriteKitchens
from kitchen.models import Kitchens, Categories, Menus, Items, SubItems, Reviews
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.http import HttpResponse, JsonResponse
from django.db.models import Avg, Q
import http.client


def index(request):
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
			if dist <= i.visibilityRadius:
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


def favouriteKitchens(request):
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
	else:
		FavouriteKitchens.objects.filter(id=fav.id).delete()


def Menu(request, pk=None):
	fav = FavouriteKitchens.objects.filter(customer_id=request.user.id, kitchen_id=pk).first()
	if fav == None:
		favourite = False
	else:
		favourite = True
	categories = Categories.objects.filter(kit_id=pk)
	menu = Menus.objects.filter(kit_id=pk)
	kitchen = Kitchens.objects.filter(id=pk)

	cartitemcount = countCartItems(request)
	
	items = []
	for i in menu:
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
			temp.append(i.offer)
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
	cartitemcount = countCartItems(request)
	addform = UserAddressesForm(request.POST or None)
	
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
		menu = Menus.objects.filter(kit_id=request.COOKIES['kit'])
		items = []
		subtotal = 0
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
					total_price = item[0].price*int(quant)
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
							total_price = sub.price*int(quant)
							subtotal = subtotal + total_price
							temp.append(total_price)
							temp.append(str(item[0].id)+"-"+str(sub.id))
							temp.append(i.minOrder)
							items.append(temp)
		
		total = subtotal + 20
		context = {
			'items': items,
			'subtotal': subtotal,
			'kitchen': kitchen,
			'total': total,
			'cartitemcount': cartitemcount,
			'addressform': addform,
			'addresses': addresses,
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


def updateProfile(request):
	form = CustomerUserProfileForm(request.POST or None, instance=request.user)
	print(request.POST)
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


def Checkout(request):
	print("checkout")
	addid = request.POST['address']
	deladdress = Addresses.objects.filter(id=addid)
	kitid = request.COOKIES['kit']
	kitchen = Kitchens.objects.filter(id=kitid)

	distance=deladdress[0].location.distance(kitchen[0].location) * 100
	if distance > 3:
		return JsonResponse({"error_message": 'This Kitchen does not deliver to this location.'}, status=200)
	pass


@login_required(login_url='/login/')
def orders(request):
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
	print(request.POST)
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



def orderStatus(request, pk=None):
	context = {
		'order': Order.objects.filter(id=pk)[0],
	}
	return render(request, 'orderStatus.html', context)


# def sendOTP(request):

# 	conn = http.client.HTTPSConnection("d7sms.p.rapidapi.com")

# 	payload = "{\n    \"coding\": \"8\",\n    \"from\": \"SMSInfo\",\n    \"hex-content\": \"00480065006c006c006f\",\n    \"to\": 9582270031\n}"

# 	headers = {
# 		'content-type': "application/json",
# 		'authorization': "Basic c2phaW5odWI6c2phaW5odWIxOTk1",
# 		'x-rapidapi-key': "801da32802msh5a6b81ed8c0336cp125b90jsncd7649e27e3d",
# 		'x-rapidapi-host': "d7sms.p.rapidapi.com"
# 		}

# 	conn.request("POST", "/secure/send", payload, headers)

# 	res = conn.getresponse()
# 	data = res.read()

# 	print(data.decode("utf-8"))


def Contact(request):
	return render(request, 'contact.html')
