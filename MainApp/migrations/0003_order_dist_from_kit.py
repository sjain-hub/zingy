# Generated by Django 2.2 on 2021-01-20 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0002_auto_20201222_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='dist_from_kit',
            field=models.FloatField(default=0.0),
        ),
    ]