from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


class Folder(models.Model):
    name = models.CharField(max_length=200)
    owner_id = models.IntegerField()

    # a parent folder id of null/blank would indicate a root folder.
    # A users root folder is created upon registration
    parent_folder_id = models.IntegerField(blank=True, null=True)
    date_created = models.DateTimeField(default=datetime.now)

    is_recycled = models.BooleanField(default=False)
    date_recycled = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.name


class File(models.Model):
    name = models.CharField(max_length=200)
    parent_folder_id = models.IntegerField()

    file_source = models.FileField(upload_to='uploads/%Y/%m/%d/')
    owner_id = models.IntegerField()

    # For now - filetype is just extracted from the uploaded file name
    file_type = models.CharField(max_length=20)

    # more like date added. We will leave it for consistency
    date_created = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.name


# #change upload fields to use this shit.
# def user_directory_path(instance, filename):
#     # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
#     return 'user_{0}/{1}'.format(instance.user.id, filename)

# class MyModel(models.Model):
#     upload = models.FileField(upload_to=user_directory_path)
