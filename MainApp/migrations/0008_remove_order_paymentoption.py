# Generated by Django 2.2 on 2021-08-14 12:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0007_auto_20210813_1222'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='paymentOption',
        ),
    ]
