# Generated by Django 2.2 on 2021-02-09 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0002_auto_20210206_1124'),
    ]

    operations = [
        migrations.CreateModel(
            name='Queries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
                ('phone', models.CharField(blank=True, max_length=10)),
                ('subject', models.CharField(max_length=100)),
                ('message', models.CharField(max_length=300)),
                ('reqDate', models.DateTimeField()),
                ('resDate', models.DateTimeField(blank=True)),
                ('resolved', models.BooleanField(default=False)),
                ('resolution', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
