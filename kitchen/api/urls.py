from django.urls import path
from . import views

urlpatterns = [
    path('applogin', views.login, name='applogin'),
    path('apporderList', views.orderList, name='apporderList'),
    path('appchangeOrderStatus', views.changeOrderStatus, name='appchangeOrderStatus'),
    path('appupdatePayment', views.updatePayment, name='appupdatePayment'),
]