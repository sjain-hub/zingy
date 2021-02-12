# Generated by Django 2.2 on 2021-02-12 22:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='kitchens',
            name='kitPhone',
            field=models.PositiveIntegerField(default=9873025183, unique=True, validators=[django.core.validators.MaxValueValidator(9999999999)]),
        ),
    ]
