# Generated by Django 4.2 on 2023-04-20 13:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_alter_foodintake_serving_size'),
    ]

    operations = [
        migrations.RenameField(
            model_name='foodintake',
            old_name='carbs',
            new_name='carbohydrates',
        ),
    ]
