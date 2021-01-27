from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from MainApp.forms import KitchenSignUpForm
from .forms import KitchenForm, CategoryForm, ItemForm, SubItemForm, MenuForm
from django.contrib.auth.decorators import login_required
from .models import Kitchens, Items, SubItems, Categories, Menus
from MainApp.models import Order
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.contrib.gis.geos import Point
from django.forms import inlineformset_factory
from django.db.models import Q, DateTimeField
from datetime import datetime, timedelta, date
import calendar



@login_required(login_url='/kitLogin/')
def kitchenHomePage(request, pk=None):
	if not request.user.is_authenticated:
		return redirect("kitchenLogin")

	if request.user.kit_Created:
		kitchen = request.user.kitchens
		menuFormset = inlineformset_factory(Kitchens, Menus, form=MenuForm, extra=1)
		items = Items.objects.filter(
			kit_id=request.user.kitchens.id).order_by('category')
		categories = Categories.objects.filter(kit_id=request.user.kitchens.id)
		# menus = Menus.objects.filter(kit_id=request.user.kitchens.id)

		# if request.POST:
		# 	for menu in menus:
		# 		menu.delete()
		# 	for item in items:
		# 		tick = 'tick' + str(item.id)
		# 		radio = 'radio' + str(item.id)
		# 		offer = 'offer' + str(item.id)
		# 		minorder = 'minOrder' + str(item.id)
		# 		if tick in request.POST:
		# 			menu = Menus()
		# 			menu.item = item
		# 			menu.kit = request.user.kitchens
		# 			if not request.POST[offer] == '':
		# 				menu.offer = request.POST[offer]
		# 			if not request.POST[minorder] == '':
		# 				menu.minOrder = request.POST[minorder]
		# 			if radio in request.POST:
		# 				menu.out_of_stock = False
		# 			else:
		# 				menu.out_of_stock = True
		# 			menu.save()
		if request.POST:
			menuformset = menuFormset(request.POST or None, form_kwargs={'user': request.user}, instance=kitchen)
			if menuformset.is_valid():
				menuformset.save()
				formset = menuFormset(form_kwargs={'user': request.user}, instance=kitchen)
				return render(request, 'menuFormModal.html', {"menuform": formset} )
			else:
				return render(request, 'menuFormModal.html', {"menuform": menuformset} )

		menus = Menus.objects.filter(kit_id=request.user.kitchens.id)
		tuple_menu = ()
		l = list(tuple_menu)
		for x in menus:
			l.append(x.item.id)
		menuitems = Items.objects.filter(id__in=tuple(l)).order_by('category')

		# tuple_item = ()
		# k = list(tuple_item)
		# for x in items:
		# 	if not x.id in tuple(l):
		# 		k.append(x.id)
		# queryset = Items.objects.filter(id__in=tuple(k))
		# print(queryset)
		formset = menuFormset(form_kwargs={'user': request.user}, instance=kitchen)

		waitingorderscount = countWaitingOrders(request)

		context = {
			"menuform": formset,
			'items': items,
			'categories': categories,
			'menuitems': menuitems,
			'waitingorderscount': waitingorderscount
		}

		return render(request, 'kitHome.html', context)


def handleStatus(request):
	kitform = KitchenForm(instance=request.user.kitchens, user=request.user)
	kitinstance = kitform.save(commit=False)
	if kitinstance.status == "Open":
		kitinstance.status = "Closed"
	else:
		kitinstance.status = "Open"
	kitinstance.save()


@login_required(login_url='/kitLogin/')
def createKitchen(request):
	if not request.user.kit_Created:
		kitform = KitchenForm(request.POST or None,
		                      request.FILES or None, user=request.user)
		userform = KitchenSignUpForm(instance=request.user)
		if kitform.is_valid():
			print("entered")
			lon = kitform.cleaned_data['longitude']
			lat = kitform.cleaned_data['latitude']

			kitinstance = kitform.save(commit=False)
			kitinstance.location = Point(lon, lat, srid=4326)
			kitinstance.user = request.user
			kitinstance.status = "Closed"
			kitinstance.registrationDate = datetime.now()
			kitinstance.save()

			userinstance = userform.save(commit=False)
			userinstance.kit_Created = True
			userinstance.save()

			return redirect("kitchenHomePage")
		context = {
			'form': kitform,
		}
		return render(request, 'createKit.html', context)


@login_required(login_url='/kitLogin/')
def updateKitchen(request):
	kitform = KitchenForm(request.POST or None, request.FILES or None,
	                      instance=request.user.kitchens, user=request.user)
	if request.POST:
		print(kitform.errors)
		if kitform.is_valid():
			kitform.save()
			return redirect("kitchenHomePage")
	waitingorderscount = countWaitingOrders(request)
	context = {
		'form': kitform,
		'waitingorderscount': waitingorderscount
	}
	return render(request, 'createKit.html', context)


@login_required(login_url='/kitLogin/')
def addFoodItems(request):
	if not request.user.is_authenticated:
		return redirect("kitchenLogin")

	kitchen = request.user.kitchens
	itemFormset = inlineformset_factory(Kitchens, Items, form=ItemForm, extra=1)
	subItemFormset = inlineformset_factory(
		Items, SubItems, form=SubItemForm, extra=1)
	categoryFormset = inlineformset_factory(
		Kitchens, Categories, form=CategoryForm, extra=1)

	# item = Items.objects.filter(id=1)
	# SIformset = subItemFormset(instance=item[0])
	SIformset = ''

	if request.POST:
		# print(request.POST)
		if 'submit' in request.POST.keys():
			type = request.POST['submit']
			if type == "Add/Update Items":
				print("item")
				formset = itemFormset(request.POST or None, request.FILES or None, form_kwargs={
				                      'user': request.user}, instance=kitchen)
				if formset.is_valid():
					for form in formset.forms:
						print(form.cleaned_data)
					formset.save()
			elif type == "Save":
				print("cat")
				catformset = categoryFormset(request.POST or None, instance=kitchen)
				if catformset.is_valid():
					catformset.save()
			elif type == "Add/Update SubItems":
				itemid = request.POST['itemId']
				item = Items.objects.filter(id=itemid)
				SIformset = subItemFormset(request.POST or None, instance=item[0])
				if SIformset.is_valid():
					SIformset.save()
		else:

			itemid = request.POST['itemId']
			item = Items.objects.filter(id=itemid)
			SIformset = subItemFormset(instance=item[0])
			return render(request, 'subItemsModal.html', {"subItems": SIformset} )

	queryset = Items.objects.order_by('category')
	formset = itemFormset(
		form_kwargs={'user': request.user}, instance=kitchen, queryset=queryset)

	catformset = categoryFormset(instance=kitchen)

	waitingorderscount = countWaitingOrders(request)

	context = {
			"existing": formset,
			"cat": catformset,
			"subItems": SIformset,
			"waitingorderscount": waitingorderscount
		}
	return render(request, 'addFoodItems.html', context)


@login_required(login_url='/kitLogin/')
def orderList(request):
	# if request.POST:
	# 	oid = request.POST['orderid']
	# 	select = request.POST['status']
	# 	# order = Order.objects.filter(id=oid)
	# 	print(oid, select)
	# 	Order.objects.filter(id=int(oid)).update(status=select, completed_at=datetime.now())

	orders = Order.objects.filter(kitchen_id=request.user.kitchens.id).order_by("scheduled_order")

	for i in orders:
		i.itemswithquantity = i.itemswithquantity.split(",")
	
	days = []
	todaysDate = datetime.today().date()
	days.append(todaysDate - timedelta(days=1))
	days.append(todaysDate)
	days.append(todaysDate + timedelta(days=1))
	days.append(todaysDate + timedelta(days=2))
	
	context = {
		'orders': orders,
		'waitingorderscount': orders.filter(status='Waiting').count(),
		'days': days,
	}
	return render(request, 'orderList.html', context)


@login_required(login_url='/kitLogin/')
def orderHistory(request):
	print(request.COOKIES)

	todaysDate = datetime.today().date()
	registrationDateOfKitchen = request.user.kitchens.registrationDate
	years = getYears(registrationDateOfKitchen)

	if 'year' in request.COOKIES.keys():
		year = int(request.COOKIES['year'])
		months = getMonths(year, registrationDateOfKitchen)
		if 'month' in request.COOKIES.keys():
			month = datetime.strptime(request.COOKIES['month'], "%B").month
			orders = Order.objects.filter(kitchen_id=request.user.kitchens.id, created_at__month=month, created_at__year=year).order_by("created_at")
			days = days_in_month(month, year)
		else:
			month = datetime.strptime(months[0], "%B").month
			orders = Order.objects.filter(kitchen_id=request.user.kitchens.id, created_at__month=month, created_at__year=year).order_by("created_at")
			days = days_in_month(month, year)
	else:
		year = todaysDate.year
		month = todaysDate.month
		months = getMonths(year, registrationDateOfKitchen)
		orders = Order.objects.filter(kitchen_id=request.user.kitchens.id, created_at__month=month, created_at__year=year).order_by("created_at")
		days = days_in_month(month, year)

	monthHistory = []
	dayWiseOrders = []

	monthTotal = 0
	for day in days:
		temp = []
		dayTotal = 0
		temp.append(day)
		orderstemp = []
		for todayOrder in orders:
			if todayOrder.created_at.date() == day:
				todayOrder.itemswithquantity = todayOrder.itemswithquantity.split(",")
				orderstemp.append(todayOrder)
				if todayOrder.status == "Delivered" or todayOrder.status == "Picked":
					monthTotal = monthTotal + todayOrder.total_amount
					dayTotal = dayTotal + todayOrder.total_amount
		temp.append(orderstemp)
		temp.append(dayTotal)
		dayWiseOrders.append(temp)

	monthHistory.append(dayWiseOrders)
	monthHistory.append(monthTotal)
	# print(monthHistory, "monthHistory")

	context = {
		'monthHistory': monthHistory,
		'waitingorderscount': countWaitingOrders(request),
		'years': years,
		'months': months,
		'selectedyear': year,
		'selectedmonth': calendar.month_name[month],
	}
	return render(request, 'orderHistory.html', context)


def days_in_month(m, y):
	if m < 12:
		ndays = (date(y, m+1, 1) - date(y, m, 1)).days
	else:
		ndays = (date(y+1, 1, 1) - date(y, m, 1)).days
	d1 = date(y, m, 1)
	d2 = date(y, m, ndays)
	delta = d2 - d1
	return [(d1 + timedelta(days=i)) for i in range(delta.days + 1)]

def getYears(kitregdate):
	y = datetime.now()
	kitregyear = kitregdate.year
	delta = y.year-kitregyear
	return [(kitregyear + i) for i in range(delta + 1)]


def getMonths(year, kitregdate):
	if year == datetime.now().year:
		return [(calendar.month_name[i+1]) for i in range(datetime.now().month)]
	elif year == kitregdate.year:
		return [(calendar.month_name[i+kitregdate.month]) for i in range(13 - kitregdate.month)]
	else:
		return [(calendar.month_name[i+1]) for i in range(12)]


def countWaitingOrders(request):
	count = Order.objects.filter(kitchen_id=request.user.kitchens.id, status='Waiting').count()
	return count