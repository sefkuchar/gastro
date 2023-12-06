# Generated by Django 4.1.13 on 2023-12-06 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gastro', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='role',
            field=models.CharField(choices=[('A', 'admin'), ('O', 'Owner'), ('W', 'Waiter'), ('C', 'Customer')], default='C', max_length=9),
        ),
    ]