# Generated by Django 2.2.2 on 2019-06-21 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20190620_1025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userquota',
            name='current_usage_mb',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
        migrations.AlterField(
            model_name='userquota',
            name='max_usage_mb',
            field=models.DecimalField(decimal_places=2, default=1000, max_digits=7),
        ),
    ]
