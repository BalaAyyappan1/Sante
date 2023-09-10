# Generated by Django 4.2 on 2023-04-19 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_userprofile_activity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='goal',
            field=models.CharField(choices=[('L', 'Lose'), ('G', 'Gain'), ('M', 'Maintain')], default='M', max_length=15),
        ),
    ]