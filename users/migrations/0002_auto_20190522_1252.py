# Generated by Django 2.2.1 on 2019-05-22 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='social_id',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_password',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]