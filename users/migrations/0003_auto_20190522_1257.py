# Generated by Django 2.2.1 on 2019-05-22 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20190522_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='social_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_password',
            field=models.CharField(max_length=200, null=True),
        ),
    ]