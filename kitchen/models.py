
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.conf import settings
from datetime import date, datetime
import re
from django.db.models import DateTimeField


class DateTimeWithoutTZField(DateTimeField):
    def db_type(self, connection):
        return 'timestamp'


def get_upload_path(instance, filename):
	kitname = re.sub(r"\W+|_", ' ', instance.kitName)
	return "%s/docs/%s" % (kitname, filename)


class Kitchens(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	kitName = models.CharField(max_length=100, blank=False, unique=True)
	REST_STATE_OPEN = "Open"
	REST_STATE_CLOSE = "Closed"
	REST_STATE_CHOICES = (
		(REST_STATE_OPEN, REST_STATE_OPEN),
		(REST_STATE_CLOSE, REST_STATE_CLOSE)
	)
	status = models.CharField(
		max_length=50, choices=REST_STATE_CHOICES, default=REST_STATE_CLOSE, blank=False)
	Delivery = "Delivery"
	PickUp = "PickUp"
	MODE_CHOICES = (
		(Delivery, Delivery),
		(PickUp, PickUp)
	)
	mode = models.CharField(
		max_length=50, choices=MODE_CHOICES, default=PickUp, blank=False)
	address = models.TextField(max_length=200, blank=False)
	Delhi = "Delhi"
	Noida = "Noida"
	CITY_CHOICES = (
		(Delhi, Delhi),
		(Noida, Noida)
	)
	city = models.CharField(max_length=50, choices=CITY_CHOICES, blank=False)
	landmark = models.CharField(max_length=50, blank=False)
	postalCode = models.CharField(max_length=6, blank=False)
	floorNo = models.CharField(max_length=2, blank=False)
	latitude = models.FloatField(blank=False)
	longitude = models.FloatField(blank=False)
	location = models.PointField(default=Point(0.0, 0.0))
	dp = models.ImageField(upload_to=get_upload_path, blank=False)
	video = models.FileField(upload_to=get_upload_path, blank=False)
	fssaiLicNo = models.CharField(blank=False, unique=True, max_length=14)
	fssaiName = models.CharField(max_length=50, blank=False)
	fssaiAdd = models.TextField(max_length=200, blank=False)
	fssaiExpiry = models.DateField(default=date.today)
	fssaiCerti = models.FileField(upload_to=get_upload_path, blank=False)
	kyc = models.FileField(upload_to=get_upload_path, blank=False)
	degree = models.FileField(upload_to=get_upload_path, blank=True)
	approved = models.BooleanField(default=False)
	description = models.TextField(max_length=500, blank=True)
	acceptAdvcOrders = models.BooleanField(default=False)
	deliveryTime = models.IntegerField(blank=False, default=45)
	visibilityRadius = models.FloatField(blank=False, default=2.0)
	pureVeg = models.BooleanField(default=False)
	registrationDate = DateTimeWithoutTZField(blank=False)

	def __str__(self):
		return self.kitName + ", by : " + self.user.username


def get_upload_path_food(instance, filename):
	kitname = re.sub(r"\W+|_", ' ', instance.kit.kitName)
	return "%s/foodImages/%s" % (kitname, filename)


class Categories(models.Model):
	kit = models.ForeignKey(Kitchens, on_delete=models.CASCADE)
	category = models.CharField(max_length=50, blank=False)

	def __str__(self):
		return self.category


class Items(models.Model):
	kit = models.ForeignKey(Kitchens, on_delete=models.CASCADE)
	category = models.ForeignKey(Categories, on_delete=models.CASCADE)
	itemName = models.CharField(max_length=30, blank=False)
	Veg = "veg"
	NonVeg = "nonveg"
	TYPE_CHOICES = (
		(Veg, Veg),
		(NonVeg, NonVeg)
	)
	itemType = models.CharField(max_length=50, choices=TYPE_CHOICES, default=Veg, blank=False)
	price = models.IntegerField(blank=False)
	image = models.ImageField(upload_to=get_upload_path_food, blank=False)
	condition = models.TextField(max_length=50, blank=True)
	itemDesc = models.TextField(max_length=50, blank=True)

	def __str__(self):
		return self.itemName


class SubItems(models.Model):
	item = models.ForeignKey(Items, on_delete=models.CASCADE)
	name = models.CharField(max_length=30, blank=False)
	price = models.IntegerField(blank=False)

	def __str__(self):
		return self.name


class Menus(models.Model):
	item = models.OneToOneField(Items, on_delete=models.CASCADE)
	kit = models.ForeignKey(Kitchens, on_delete=models.CASCADE)
	offer = models.IntegerField(blank=True, default=0)
	out_of_stock = models.BooleanField(default=False)
	minOrder = models.IntegerField(blank=False,default=0)

	def __str__(self):
		return self.item.itemName+' - '+self.kit.kitName


class Reviews(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	kit = models.ForeignKey(Kitchens, on_delete=models.CASCADE)
	ratings = models.IntegerField(blank=True, default=0)
	reviews = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return self.kit.kitName
