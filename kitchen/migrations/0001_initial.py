# Generated by Django 2.2 on 2021-07-17 19:20

import datetime
from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
from django.db import migrations, models
import django.db.models.deletion
import kitchen.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('MainApp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Items',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('itemName', models.CharField(max_length=30)),
                ('itemType', models.CharField(choices=[('veg', 'veg'), ('nonveg', 'nonveg')], default='veg', max_length=50)),
                ('price', models.IntegerField()),
                ('image', models.ImageField(upload_to=kitchen.models.get_upload_path_food)),
                ('condition', models.TextField(blank=True, max_length=50)),
                ('itemDesc', models.TextField(blank=True, max_length=50)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kitchen.Categories')),
            ],
        ),
        migrations.CreateModel(
            name='Kitchens',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kitName', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(choices=[('Open', 'Open'), ('Closed', 'Closed')], default='Closed', max_length=50)),
                ('mode', models.CharField(choices=[('Delivery', 'Delivery'), ('PickUp', 'PickUp')], default='PickUp', max_length=50)),
                ('address', models.TextField(max_length=200)),
                ('city', models.CharField(choices=[('Delhi', 'Delhi'), ('Noida', 'Noida')], max_length=50)),
                ('landmark', models.CharField(max_length=50)),
                ('postalCode', models.CharField(max_length=6)),
                ('floorNo', models.CharField(max_length=2)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('location', django.contrib.gis.db.models.fields.PointField(default=django.contrib.gis.geos.point.Point(0.0, 0.0), srid=4326)),
                ('dp', models.ImageField(upload_to=kitchen.models.get_upload_path)),
                ('chefDp', models.ImageField(upload_to=kitchen.models.get_upload_path)),
                ('video', models.FileField(upload_to=kitchen.models.get_upload_path)),
                ('fssaiLicNo', models.CharField(max_length=14, unique=True)),
                ('fssaiName', models.CharField(max_length=50)),
                ('fssaiAdd', models.TextField(max_length=200)),
                ('fssaiExpiry', models.DateField(default=datetime.date.today)),
                ('fssaiCerti', models.FileField(upload_to=kitchen.models.get_upload_path)),
                ('kyc', models.FileField(upload_to=kitchen.models.get_upload_path)),
                ('degree', models.FileField(blank=True, upload_to=kitchen.models.get_upload_path)),
                ('approved', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True, max_length=500)),
                ('wantAdvancePayment', models.BooleanField(default=False)),
                ('acceptAdvcOrders', models.BooleanField(default=False)),
                ('deliveryTime', models.IntegerField(default=45)),
                ('deliveryCharge', models.IntegerField(default=25)),
                ('visibilityRadius', models.FloatField(default=2.0)),
                ('pureVeg', models.BooleanField(default=False)),
                ('registrationDate', models.DateTimeField()),
                ('subscriptionExpiry', models.DateTimeField()),
                ('subscriptionExpired', models.BooleanField(default=False)),
                ('paytmLink', models.CharField(max_length=30)),
                ('paytmNo', models.CharField(max_length=10, unique=True)),
                ('QRCode', models.ImageField(upload_to=kitchen.models.get_upload_path)),
                ('youTubeReview', models.TextField(blank=True, max_length=500)),
                ('youTubeLink', models.CharField(blank=True, max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PlanList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('days', models.IntegerField()),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='UserDiscountCoupons',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issueDate', models.DateTimeField()),
                ('validTill', models.DateTimeField()),
                ('discount', models.IntegerField()),
                ('redeemed', models.BooleanField(default=False)),
                ('description', models.CharField(blank=True, max_length=100)),
                ('code', models.CharField(max_length=15)),
                ('maxDiscount', models.IntegerField(blank=True)),
                ('kit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kitchen.Kitchens')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SubItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('price', models.IntegerField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kitchen.Items')),
            ],
        ),
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ratings', models.IntegerField(blank=True, default=0)),
                ('reviews', models.CharField(blank=True, max_length=200)),
                ('kit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kitchen.Kitchens')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pack_name', models.CharField(max_length=30)),
                ('recharge_date', models.DateTimeField()),
                ('amount', models.IntegerField()),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('status', models.CharField(max_length=30)),
                ('kit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kitchen.Kitchens')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kitchen.PlanList')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Menus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offer', models.IntegerField(default=0)),
                ('out_of_stock', models.BooleanField(default=False)),
                ('minOrder', models.IntegerField(default=0)),
                ('item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='kitchen.Items')),
                ('kit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kitchen.Kitchens')),
            ],
        ),
        migrations.AddField(
            model_name='items',
            name='kit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kitchen.Kitchens'),
        ),
        migrations.CreateModel(
            name='ComplaintsAndRefunds',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_date', models.DateTimeField()),
                ('closing_date', models.DateTimeField(null=True)),
                ('subject', models.CharField(blank=True, max_length=50)),
                ('issue', models.CharField(blank=True, max_length=400)),
                ('status', models.CharField(choices=[('Under Process', 'Under Process'), ('Closed', 'Closed')], default='Under Process', max_length=20)),
                ('paytmNo', models.CharField(blank=True, max_length=10)),
                ('comments', models.CharField(blank=True, max_length=200)),
                ('kit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kitchen.Kitchens')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MainApp.Order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='categories',
            name='kit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kitchen.Kitchens'),
        ),
    ]
