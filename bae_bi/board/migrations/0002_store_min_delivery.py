# Generated by Django 4.1 on 2023-10-11 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='min_delivery',
            field=models.IntegerField(default=0),
        ),
    ]
