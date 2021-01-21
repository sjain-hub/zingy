from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('kitchens/', views.nearbyKitchens, name='kitchens'),
    path('kitchens/menu/<int:pk>/', views.Menu, name='menu'),
    path('cart/', views.Cart, name='cart'),
    path('login/', views.Login, name='login'),
    path('register/', views.Register, name='register'),
    path('kitRegister/', views.kitchenRegistration, name='kitchenRegistration'),
    path('kitLogin/', views.kitchenLogin, name='kitchenLogin'),
    path('contact/', views.Contact, name='contact'),
    path('logout/', views.Logout, name='logout'),
    path('test/', views.test, name='test'),
    path('checkout/', views.Checkout, name='checkout'),
    path('kitchen/', include('kitchen.urls')),
    path('orders/', views.orders, name='orders'),
    path('addReview/', views.addReview, name='addReview'),
    path('orderStatus/<int:pk>/', views.orderStatus, name='orderStatus'),
]