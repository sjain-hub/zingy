# Generated by Django 2.2 on 2021-02-17 22:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kitchen', '0021_auto_20210215_2305'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDiscountCoupons',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issueDate', models.DateTimeField()),
                ('validTill', models.DateTimeField()),
                ('validity', models.IntegerField()),
                ('discount', models.IntegerField()),
                ('redeemed', models.BooleanField(default=False)),
                ('description', models.CharField(blank=True, max_length=100)),
                ('code', models.CharField(max_length=6)),
                ('maxDiscount', models.IntegerField(blank=True)),
                ('kit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kitchen.Kitchens')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
