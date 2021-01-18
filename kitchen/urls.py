from django.urls import path
from . import views

urlpatterns = [
    path('createKitchen/', views.createKitchen, name='createKitchen'),
    path('updateKitchen/', views.updateKitchen, name='updateKitchen'),
    path('kitHome/', views.kitchenHomePage, name='kitchenHomePage'),
    path('addFoodItems/', views.addFoodItems, name='addFoodItems'),
    path('handleStatus/', views.handleStatus, name='handleStatus'),
    path('orderList/', views.orderList, name='orderList'),
    path('orderHistory/', views.orderHistory, name='orderHistory'),
    # path('addSubItems/', views.addSubItems, name='addSubItems'),
]