# Generated by Django 2.2 on 2021-02-14 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen', '0015_auto_20210214_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaintsandrefunds',
            name='request_date',
            field=models.DateTimeField(),
        ),
    ]