# Generated by Django 4.1 on 2023-10-16 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0008_alter_review_content_alter_review_menu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='menu',
            field=models.CharField(max_length=700, null=True),
        ),
    ]