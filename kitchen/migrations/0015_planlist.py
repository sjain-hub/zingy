# Generated by Django 2.2 on 2021-02-04 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen', '0014_paymenthistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='planList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('days', models.IntegerField()),
                ('name', models.CharField(max_length=30)),
            ],
        ),
    ]