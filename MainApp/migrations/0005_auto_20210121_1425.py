# Generated by Django 2.2 on 2021-01-21 08:55

from django.db import migrations
import kitchen.models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0004_auto_20210121_1344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='completed_at',
            field=kitchen.models.DateTimeWithoutTZField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=kitchen.models.DateTimeWithoutTZField(),
        ),
    ]