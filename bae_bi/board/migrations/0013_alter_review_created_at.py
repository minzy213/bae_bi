# Generated by Django 4.1 on 2023-10-17 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0012_rename_add_dc_delivery_info_fee_list_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='created_at',
            field=models.CharField(default='', max_length=255, null=True),
        ),
    ]
