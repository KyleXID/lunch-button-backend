# Generated by Django 2.2.1 on 2019-05-27 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0002_auto_20190527_0458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='community',
            name='zip_code',
            field=models.CharField(db_index=True, max_length=45),
        ),
    ]
