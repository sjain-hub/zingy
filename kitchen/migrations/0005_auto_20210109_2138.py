# Generated by Django 2.2 on 2021-01-09 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen', '0004_kitchens_registrationdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kitchens',
            name='registrationDate',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
