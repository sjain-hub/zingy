# Generated by Django 2.2 on 2021-02-09 14:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen', '0003_auto_20210209_1932'),
    ]

    operations = [
        migrations.AddField(
            model_name='kitchens',
            name='registrationDate',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 9, 19, 34, 41, 940147)),
        ),
        migrations.AddField(
            model_name='kitchens',
            name='subscriptionExpiry',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 9, 19, 34, 41, 940164)),
        ),
        migrations.AddField(
            model_name='paymenthistory',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 9, 19, 34, 41, 942712)),
        ),
        migrations.AddField(
            model_name='paymenthistory',
            name='recharge_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 9, 19, 34, 41, 942685)),
        ),
        migrations.AddField(
            model_name='paymenthistory',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 9, 19, 34, 41, 942704)),
        ),
    ]
