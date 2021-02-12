# Generated by Django 2.2 on 2021-02-13 00:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen', '0010_kitchens_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kitchens',
            name='phone_number',
            field=models.CharField(blank=True, max_length=10, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^[6-9]\\d{9}$')]),
        ),
    ]
