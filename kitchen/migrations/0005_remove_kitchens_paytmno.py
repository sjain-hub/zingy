# Generated by Django 2.2 on 2021-02-12 22:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen', '0004_kitchens_paytmno'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kitchens',
            name='paytmNo',
        ),
    ]
