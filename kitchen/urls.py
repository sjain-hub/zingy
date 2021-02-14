from django.urls import path
from . import views

urlpatterns = [
    path('', views.kitchenHomePage, name='kitchenHomePage'),
    path('kitRegister/', views.kitchenUserRegistration, name='kitchenRegistration'),
    path('updateKitUserProfile/', views.updateKitUserProfile, name='updateKitUserProfile'),
    path('kitLogin/', views.kitchenLogin, name='kitchenLogin'),
    path('createKitchen/', views.createKitchen, name='createKitchen'),
    path('updateKitchen/', views.updateKitchen, name='updateKitchen'),
    path('addFoodItems/', views.addFoodItems, name='addFoodItems'),
    path('handleStatus/', views.handleStatus, name='handleStatus'),
    path('orderList/', views.orderList, name='orderList'),
    path('orderHistory/', views.orderHistory, name='orderHistory'),
    path('subscription/', views.subscription, name='subscription'),
    path('paymentHistory/', views.paymentHistory, name='paymentHistory'),
    path('complaintsAndRefunds/', views.complaintsAndRefunds, name='complaintsAndRefunds'),
    path('handlePaytmResponse/', views.handlePaytmResponse, name='handlePaytmResponse'),
    # path('addSubItems/', views.addSubItems, name='addSubItems'),
]