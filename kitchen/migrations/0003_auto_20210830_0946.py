# Generated by Django 2.2 on 2021-08-30 09:46

from django.db import migrations, models
import kitchen.models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen', '0002_auto_20210731_0930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='items',
            name='image',
            field=models.ImageField(blank=True, upload_to=kitchen.models.get_upload_path_food),
        ),
    ]