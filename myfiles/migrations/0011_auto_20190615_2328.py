# Generated by Django 2.2.2 on 2019-06-15 21:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myfiles', '0010_auto_20190615_2244'),
    ]

    operations = [
        migrations.RenameField(
            model_name='folder',
            old_name='owner_id',
            new_name='owner',
        ),
        migrations.RenameField(
            model_name='folder',
            old_name='parent_folder_id',
            new_name='parent_folder',
        ),
    ]
