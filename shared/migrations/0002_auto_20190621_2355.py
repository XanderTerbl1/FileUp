# Generated by Django 2.2.2 on 2019-06-21 21:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sharedfolder',
            name='folder',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='myfiles.Folder'),
        ),
    ]