# Generated by Django 2.2 on 2021-08-13 12:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0004_auto_20210813_0914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_addr',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MainApp.Addresses'),
        ),
    ]