# Generated by Django 5.1.2 on 2024-10-29 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='private_key',
            field=models.CharField(max_length=90),
        ),
    ]