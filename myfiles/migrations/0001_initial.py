# Generated by Django 2.2.2 on 2019-06-12 15:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('parent_folder_id', models.IntegerField()),
                ('file_source', models.FileField(upload_to='uploads/%Y/%m/%d/')),
                ('owner_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('owner_id', models.IntegerField()),
                ('parent_folder_id', models.IntegerField(blank=True, null=True)),
                ('date_created', models.DateTimeField(blank=True, default=datetime.datetime.now)),
            ],
        ),
    ]