# Generated by Django 4.1 on 2023-10-16 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0009_alter_review_menu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='info',
            field=models.CharField(max_length=300, null=True),
        ),
    ]