
from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from kitchen.models import Kitchens, Menus, DateTimeWithoutTZField as DateTimeField
from django.contrib.gis.geos import Point
from django.db.models import Q


class User(AbstractUser):
	is_customer = models.BooleanField(default=False)
	is_kitchen = models.BooleanField(default=False)
	phone = models.CharField(max_length=10, blank=False, default="", unique=True)
	email = models.EmailField(unique=True, blank=False)
	kit_Created = models.BooleanField(default=False)


class Addresses(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
	place = models.CharField(max_length=30, blank=False)
	latitude = models.FloatField(blank=False)
	longitude = models.FloatField(blank=False)
	location = models.PointField(default=Point(0.0, 0.0))
	address = models.CharField(max_length=200, blank=False)
	floorNo = models.CharField(max_length=2, blank=False)

	def __str__(self):
		return self.user.username + "  " + self.place
	
class Order(models.Model):
	id 				  = models.AutoField(primary_key=True)
	total_amount      = models.IntegerField(default=0)
	created_at        = DateTimeField(blank=False)
	completed_at 	  = DateTimeField(null=True, blank=True)
	scheduled_order   = DateTimeField(null=True, blank=True)
	mode 			  = models.CharField(max_length=50,blank=True)
	itemswithquantity = models.CharField(max_length=300,blank=True)
	delivery_addr     = models.CharField(max_length=50,blank=True)
	dist_from_kit     = models.FloatField(default=0.0)
	message			  = models.CharField(max_length=100,blank=True)
	msgtocust		  = models.CharField(max_length=100,blank=True)
	customer          = models.ForeignKey(User ,on_delete=models.CASCADE)
	kitchen			  = models.ForeignKey(Kitchens ,on_delete=models.CASCADE)
	
	ORDER_STATE_WAITING 	 = "Waiting"
	ORDER_STATE_PLACED 		 = "Placed"
	ORDER_STATE_PACKED		 = "Packed"
	ORDER_STATE_PREPARING	 = "Preparing"
	ORDER_STATE_PICKED		 = "Picked"
	ORDER_STATE_CANCELLED    = "Cancelled"
	ORDER_STATE_REJECTED     = "Rejected"
	ORDER_STATE_DISPATCHED   = "Dispatched"
	ORDER_STATE_DELIVERED    = "Delivered"

	ORDER_STATE_CHOICES = (
		(ORDER_STATE_WAITING,ORDER_STATE_WAITING),
	    (ORDER_STATE_PLACED, ORDER_STATE_PLACED),
	    (ORDER_STATE_PACKED, ORDER_STATE_PACKED),
		(ORDER_STATE_PREPARING, ORDER_STATE_PREPARING),
	    (ORDER_STATE_CANCELLED, ORDER_STATE_CANCELLED),
	    (ORDER_STATE_DISPATCHED, ORDER_STATE_DISPATCHED),
		(ORDER_STATE_DELIVERED, ORDER_STATE_DELIVERED),
		(ORDER_STATE_PICKED, ORDER_STATE_PICKED),
		(ORDER_STATE_REJECTED, ORDER_STATE_REJECTED)
	)
	status = models.CharField(max_length=50,choices=ORDER_STATE_CHOICES,default=ORDER_STATE_WAITING)
	
	def __str__(self):
		return str(self.id) +' '+self.status


class FavouriteKitchens(models.Model):
	customer          = models.ForeignKey(User ,on_delete=models.CASCADE)
	kitchen			  = models.ForeignKey(Kitchens ,on_delete=models.CASCADE)

	def __str__(self):
		return str(self.customer.first_name) +' => '+self.kitchen.kitName