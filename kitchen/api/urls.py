from django.urls import path
from . import views

urlpatterns = [
    path('applogin', views.login, name='applogin'),
    path('apporderList', views.orderList, name='apporderList'),
]