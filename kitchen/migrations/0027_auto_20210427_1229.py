# Generated by Django 2.2 on 2021-04-27 12:29

from django.db import migrations, models
import kitchen.models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen', '0026_auto_20210427_1119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kitchens',
            name='chefDp',
            field=models.ImageField(upload_to=kitchen.models.get_upload_path),
        ),
    ]
