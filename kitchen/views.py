from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import KitchenForm, CategoryForm, ItemForm, SubItemForm, MenuForm, KitchenSignUpForm, KitchenUserProfileForm
from django.contrib.auth.decorators import login_required
from .models import Kitchens, Items, SubItems, Categories, Menus, PaymentHistory, PlanList
from MainApp.models import Order, User
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.contrib.gis.geos import Point
from django.forms import inlineformset_factory
from django.db.models import Q, DateTimeField
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from celery import shared_task
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import calendar
import requests
import json
from .PayTm import Checksum


def kitchenRegistration(request):
    form = KitchenSignUpForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.is_kitchen = True
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("createKitchen")
    context = {
        'form': form
    }
    return render(request, 'kitRegister.html', context)


def updateKitUserProfile(request):
    form = KitchenUserProfileForm(request.POST or None, instance=request.user)
    if request.POST:
        if form.is_valid():
            if 'submit' in request.POST.keys():
                type = request.POST['submit']
                if type == "username":
                    User.objects.filter(id=request.user.id).update(
                        username=form.cleaned_data['username'])
                elif type == "fname":
                    User.objects.filter(id=request.user.id).update(
                        first_name=form.cleaned_data['first_name'])
                elif type == "lname":
                    User.objects.filter(id=request.user.id).update(
                        last_name=form.cleaned_data['last_name'])
                elif type == "email":
                    User.objects.filter(id=request.user.id).update(
                        email=form.cleaned_data['email'])
                elif type == "phone":
                    User.objects.filter(id=request.user.id).update(
                        phone=form.cleaned_data['phone'])
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
                        return render(request, 'kitUserProfile.html', context)
                    user.set_password(password)
                    user.save()
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        if user.is_active:
                            login(request, user)
    context = {
            'form': form
        }
    return render(request, 'kitUserProfile.html', context)


def kitchenLogin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if user.kit_Created:
                    return redirect("kitchenHomePage")
                else:
                    return redirect("createKitchen")
            else:
                return render(request, 'kitLogin.html', {'error_message': 'Your account disable'})
        else:
            return render(request, 'kitLogin.html', {'error_message': 'Invalid Login'})
    return render(request, 'kitLogin.html')


@login_required(login_url='/kitLogin/')
def kitchenHomePage(request, pk=None):
    if request.user.kit_Created:
        kitchen = request.user.kitchens
        menuFormset = inlineformset_factory(Kitchens, Menus, form=MenuForm, extra=1)
        items = Items.objects.filter(
            kit_id=request.user.kitchens.id).order_by('category')
        categories = Categories.objects.filter(kit_id=request.user.kitchens.id)
        if request.POST:
            menuformset = menuFormset(request.POST or None, form_kwargs={
                                      'user': request.user}, instance=kitchen)
            if menuformset.is_valid():
                menuformset.save()
                formset = menuFormset(form_kwargs={'user': request.user}, instance=kitchen)
                return render(request, 'menuFormModal.html', {"menuform": formset})
            else:
                return render(request, 'menuFormModal.html', {"menuform": menuformset})

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
            lon = kitform.cleaned_data['longitude']
            lat = kitform.cleaned_data['latitude']

            kitinstance = kitform.save(commit=False)
            kitinstance.location = Point(lon, lat, srid=4326)
            kitinstance.user = request.user
            kitinstance.status = "Closed"
            currentDate = datetime.now()
            kitinstance.registrationDate = currentDate + timedelta(hours=5, minutes=30)
            kitinstance.subscriptionExpiry = currentDate.replace(hour=23, minute=59, microsecond=0) + timedelta(days=180, hours=5, minutes=30)
            kitinstance.save()

            userinstance = userform.save(commit=False)
            userinstance.kit_Created = True
            userinstance.save()

            plan = PlanList.objects.filter(days=180)[0]
            PaymentHistory.objects.create(user=request.user, kit=request.user.kitchens, pack_name=plan.name, plan=plan, recharge_date=currentDate + timedelta(hours=5, minutes=30),
                                          amount=0, start_date=currentDate + timedelta(hours=5, minutes=30), end_date=currentDate.replace(hour=23, minute=59, microsecond=0) + timedelta(days=plan.days, hours=5, minutes=30))

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
        # print(kitform.errors)
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
        if 'submit' in request.POST.keys():
            type = request.POST['submit']
            if type == "Add/Update Items":
                formset = itemFormset(request.POST or None, request.FILES or None, form_kwargs={
                                      'user': request.user}, instance=kitchen)
                if formset.is_valid():
                    formset.save()
            elif type == "Save":
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
            return render(request, 'subItemsModal.html', {"subItems": SIformset})

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

    orders = Order.objects.filter(
        kitchen_id=request.user.kitchens.id).order_by("scheduled_order")

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
    todaysDate = datetime.today().date()
    registrationDateOfKitchen = request.user.kitchens.registrationDate
    years = getYears(registrationDateOfKitchen)

    if 'year' in request.COOKIES.keys():
        year = int(request.COOKIES['year'])
        months = getMonths(year, registrationDateOfKitchen)
        if 'month' in request.COOKIES.keys():
            month = datetime.strptime(request.COOKIES['month'], "%B").month
            orders = Order.objects.filter(kitchen_id=request.user.kitchens.id,
                                          created_at__month=month, created_at__year=year).order_by("created_at")
            days = days_in_month(month, year)
        else:
            month = datetime.strptime(months[0], "%B").month
            orders = Order.objects.filter(kitchen_id=request.user.kitchens.id,
                                          created_at__month=month, created_at__year=year).order_by("created_at")
            days = days_in_month(month, year)
    else:
        year = todaysDate.year
        month = todaysDate.month
        months = getMonths(year, registrationDateOfKitchen)
        orders = Order.objects.filter(kitchen_id=request.user.kitchens.id,
                                      created_at__month=month, created_at__year=year).order_by("created_at")
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


def subscription(request):
    currentDate = datetime.now()
    expiryDate = request.user.kitchens.subscriptionExpiry
    if request.POST:
        plan = PlanList.objects.filter(id=request.POST['plan'])[0]
        if request.user.kitchens.subscriptionExpired:
            order = PaymentHistory.objects.create(user=request.user, kit=request.user.kitchens, pack_name=plan.name, plan=plan, recharge_date=currentDate + timedelta(hours=5, minutes=30),
                    amount=plan.amount, start_date=currentDate + timedelta(hours=5, minutes=30), end_date=currentDate.replace(hour=23, minute=59, microsecond=0) + timedelta(days=plan.days, hours=5, minutes=30))
        else:
            order = PaymentHistory.objects.create(user=request.user, kit=request.user.kitchens, pack_name=plan.name, plan=plan, recharge_date=currentDate + timedelta(hours=5, minutes=30),
                    amount=plan.amount, start_date=expiryDate.replace(hour=0, minute=0, microsecond=0) + timedelta(days=1, hours=5, minutes=30), end_date=expiryDate.replace(hour=23, minute=59, microsecond=0) + timedelta(days=plan.days, hours=5, minutes=30))
        param_dict = {

                'MID': settings.PAYTM_MERCHANT_ID,
                'ORDER_ID': str(order.id),
                'TXN_AMOUNT': str(plan.amount),
                'CUST_ID': str(request.user.id),
                'INDUSTRY_TYPE_ID': settings.PAYTM_INDUSTRY_TYPE_ID,
                'WEBSITE': settings.PAYTM_WEBSITE,
                'CHANNEL_ID': settings.PAYTM_CHANNEL_ID,
                'CALLBACK_URL': settings.PAYTM_CALLBACK_URL,

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, settings.PAYTM_MERCHANT_KEY)
        context = {
            'payment_url': settings.PAYTM_PAYMENT_GATEWAY_URL,
            'data_dict': param_dict
        }
        return render(request, 'paytm.html', context)

    delta = expiryDate - currentDate

    plans = PlanList.objects.filter()
    context = {
        'expiryDate': expiryDate,
        'delta': delta.days,
        'plans': plans,
    }
    return render(request, 'subscription.html', context)


@csrf_exempt
def handlePaytmResponse(request):
    resp = VerifyPaytmResponse(request)
    if resp['verified']:
        return HttpResponse("<center><h1>Transaction Successful</h1><center>", status=200)
    else:
        return HttpResponse("<center><h1>Transaction Failed</h1><center>", status=400)


def VerifyPaytmResponse(response):
    response_dict = {}
    if response.method == "POST":
        data_dict = {}
        for key in response.POST:
            data_dict[key] = response.POST[key]
        MID = data_dict['MID']
        ORDERID = data_dict['ORDERID']
        verify = Checksum.verify_checksum(data_dict, settings.PAYTM_MERCHANT_KEY, data_dict['CHECKSUMHASH'])
        order = PaymentHistory.objects.filter(id=ORDERID)[0]
        kitchen = order.kit
        plan = order.plan
        if verify:
            STATUS_URL = settings.PAYTM_TRANSACTION_STATUS_URL
            headers = {
                'Content-Type': 'application/json',
            }
            data = '{"MID":"%s","ORDERID":"%s"}'%(MID, ORDERID)
            check_resp = requests.post(STATUS_URL, data=data, headers=headers).json()
            if check_resp['STATUS']=='TXN_SUCCESS':
                Kitchens.objects.filter(id=kitchen.id).update(subscriptionExpiry = kitchen.subscriptionExpiry.replace(hour=23, minute=59, microsecond=0) + timedelta(days=plan.days, hours=5, minutes=30))
                response_dict['verified'] = True
                response_dict['paytm'] = check_resp
                return (response_dict)
            else:
                order.delete()
                response_dict['verified'] = False
                response_dict['paytm'] = check_resp
                return (response_dict)
        else:
            order.delete()
            response_dict['verified'] = False
            return (response_dict)
    response_dict['verified'] = False
    return response_dict


def paymentHistory(request):
    history = PaymentHistory.objects.filter(kit_id=request.user.kitchens).order_by("-recharge_date")
    context = {
        'history': history,
    }
    return render(request, 'paymentHistory.html', context)


#task called by celery
@shared_task
def checkKitchensValidity():
    kitchens = Kitchens.objects.filter()
    currentDate = datetime.now()
    for kitchen in kitchens:
        if currentDate >= kitchen.subscriptionExpiry:
            Kitchens.objects.filter(id=kitchen.id).update(
                subscriptionExpired=True, status="Closed")
