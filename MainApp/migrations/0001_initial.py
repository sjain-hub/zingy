# Generated by Django 2.2 on 2021-07-17 19:20

import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Addresses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.CharField(max_length=30)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('location', django.contrib.gis.db.models.fields.PointField(default=django.contrib.gis.geos.point.Point(0.0, 0.0), srid=4326)),
                ('address', models.CharField(max_length=200)),
                ('floorNo', models.CharField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='FavouriteKitchens',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('total_amount', models.IntegerField()),
                ('sub_total', models.IntegerField()),
                ('delivery_charge', models.IntegerField(blank=True)),
                ('kit_discount', models.IntegerField(blank=True)),
                ('coup_discount', models.IntegerField(blank=True)),
                ('created_at', models.DateTimeField()),
                ('completed_at', models.DateTimeField(null=True)),
                ('scheduled_order', models.DateTimeField(null=True)),
                ('mode', models.CharField(blank=True, max_length=50)),
                ('itemswithquantity', models.CharField(blank=True, max_length=300)),
                ('delivery_addr', models.CharField(blank=True, max_length=50)),
                ('dist_from_kit', models.FloatField(default=0.0)),
                ('message', models.CharField(blank=True, max_length=100)),
                ('msgtocust', models.CharField(blank=True, max_length=200)),
                ('amount_paid', models.IntegerField(default=0)),
                ('balance', models.IntegerField()),
                ('paymentOption', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('Waiting', 'Waiting'), ('Placed', 'Placed'), ('Payment', 'Payment'), ('Preparing', 'Preparing'), ('Packed', 'Packed'), ('Cancelled', 'Cancelled'), ('Dispatched', 'Dispatched'), ('Delivered', 'Delivered'), ('Picked', 'Picked'), ('Rejected', 'Rejected')], default='Waiting', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Queries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=50)),
                ('phone', models.CharField(blank=True, max_length=10)),
                ('subject', models.CharField(max_length=50)),
                ('message', models.CharField(max_length=400)),
                ('reqDate', models.DateTimeField()),
                ('resDate', models.DateTimeField(null=True)),
                ('resolved', models.BooleanField(default=False)),
                ('resolution', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_customer', models.BooleanField(default=False)),
                ('is_kitchen', models.BooleanField(default=False)),
                ('phone', models.CharField(max_length=10, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('kit_Created', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
