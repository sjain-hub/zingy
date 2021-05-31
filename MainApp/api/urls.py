from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='appindex'),
    path('appnearbyKitchens', views.nearbyKitchens, name='appnearbyKitchens'),
    path('appmenu', views.menu, name='appmenu'),
    path('appcart', views.cart, name='appcart'),
    path('appcheckuser', views.checkUser, name='appcheckuser'),
    path('applogin', views.login, name='applogin'),
    path('appregister', views.register, name='appregister'),
    path('appFetchUser', views.fetchUser, name='appFetchUser'),
    path('appUpdateProfile', views.updateProfile, name='appUpdateProfile'),
]
