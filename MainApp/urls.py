from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('kitchens/', views.nearbyKitchens, name='kitchens'),
    path('menu/<int:pk>/', views.Menu, name='menu'),
    path('add_to_favourite/<int:pk>/', views.add_to_favourite, name='add_to_favourite'),
    path('favouriteKitchens/', views.favouriteKitchens, name='favouriteKitchens'),
    path('cart/', views.Cart, name='cart'),
    path('login/', views.Login, name='login'),
    path('register/', views.Register, name='register'),
    path('updateProfile/', views.updateProfile, name='updateProfile'),
    path('logout/', views.Logout, name='logout'),
    path('test/', views.test, name='test'),
    # path('checkout/', views.Checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    path('addReview/', views.addReview, name='addReview'),
    path('sendQueries/', views.sendQueries, name='sendQueries'),
    path('orderStatus/<int:pk>/', views.orderStatus, name='orderStatus'),
    path('contactUs/', views.contactUs, name='contactUs'),
    path('updates/', views.updates, name='updates'),
    path('kitchen/', include('kitchen.urls')),
]