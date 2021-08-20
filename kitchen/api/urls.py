from django.urls import path
from . import views

urlpatterns = [
    path('applogin', views.login, name='applogin'),
    path('apporderList', views.orderList, name='apporderList'),
    path('appchangeOrderStatus', views.changeOrderStatus, name='appchangeOrderStatus'),
    path('appupdatePayment', views.updatePayment, name='appupdatePayment'),
    path('apphandleNewOrder', views.handleNewOrder, name='apphandleNewOrder'),
    path('appgetOrder', views.getOrder, name='appgetOrder'),
    path('appupdateMessageToCustomer', views.updateMessageToCustomer, name='appupdateMessageToCustomer'),
    path('apphandleKitchenStatus', views.handleKitchenStatus, name='apphandleKitchenStatus'),
]