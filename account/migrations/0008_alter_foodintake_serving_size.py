# Generated by Django 4.2 on 2023-04-20 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_rename_user_foodintake_user_profile_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodintake',
            name='serving_size',
            field=models.FloatField(default=0.0),
        ),
    ]