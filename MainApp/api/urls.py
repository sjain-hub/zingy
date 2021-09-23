from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='appindex'),
    path('appnearbyKitchens', views.nearbyKitchens, name='appnearbyKitchens'),
    path('appgetKitchen', views.getKitchen, name='appgetKitchen'),
    path('appmenu', views.menu, name='appmenu'),
    path('appcart', views.cart, name='appcart'),
    path('appcheckuser', views.checkUser, name='appcheckuser'),
    path('applogin', views.login, name='applogin'),
    path('appregister', views.register, name='appregister'),
    path('appFetchUser', views.fetchUser, name='appFetchUser'),
    path('appUpdateProfile', views.updateProfile, name='appUpdateProfile'),
    path('appGetAddresses', views.getAddresses, name='appGetAddresses'),
    path('appSaveAddress', views.saveAddress, name='appSaveAddress'),
    path('appfavouriteKitchens', views.favouriteKitchens, name='appfavouriteKitchens'),
    path('appaddToFavourite', views.add_to_favourite, name='appaddToFavourite'),
    path('apporders', views.orders, name='apporders'),
    path('appfetchOrder', views.fetchOrder, name='appfetchOrder'),
    path('appgetAndAddReviews', views.getAndAddReviews, name='appgetAndAddReviews'),
    path('appplaceOrder', views.placeOrder, name='appplaceOrder'),
    path('appcancelOrder', views.cancelOrder, name='appcancelOrder'),
    path('apporderHelp', views.orderHelp, name='apporderHelp'),
]
