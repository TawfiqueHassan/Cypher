# Generated by Django 4.1.3 on 2022-11-06 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Homepage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='Auth_Image',
            field=models.CharField(max_length=15),
        ),
    ]