# Generated by Django 2.2.2 on 2019-06-25 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myfiles', '0017_remove_folder_is_shared'),
    ]

    operations = [
        migrations.AddField(
            model_name='folder',
            name='is_shared',
            field=models.BooleanField(default=False),
        ),
    ]
