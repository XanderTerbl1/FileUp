from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


"""
Bit of redundant fields between Folder & File is better
than dealing with the problems with multi-table-inheritance. x_X
"""

class Folder(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    # a parent folder of null/blank would indicate a root folder.
    # A users root folder is created upon registration
    parent_folder = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, blank=True, null=True)
    date_created = models.DateTimeField(default=datetime.now)

    is_recycled = models.BooleanField(default=False)

    # auto updates on changes. Recycled will be last change.
    # it's a workaround - better than making custom save function
    date_recycled = models.DateTimeField(auto_now=True)

    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class File(models.Model):
    name = models.CharField(max_length=200)
    parent_folder = models.ForeignKey(Folder, on_delete=models.DO_NOTHING)

    file_source = models.FileField(upload_to='uploads/%Y/%m/%d/')
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    # For now - filetype is just extracted from the uploaded file name
    file_type = models.CharField(max_length=20)

    # more like date added. We will leave it for consistency
    date_created = models.DateTimeField(default=datetime.now, blank=True)

    is_recycled = models.BooleanField(default=False)

    # auto updates on changes. Recycled will be last change.
    # it's a workaround - better than making custom save function
    date_recycled = models.DateTimeField(auto_now=True)

    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# #change upload fields to use this shit.
# def user_directory_path(instance, filename):
#     # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
#     return 'user_{0}/{1}'.format(instance.user.id, filename)

# class MyModel(models.Model):
#     upload = models.FileField(upload_to=user_directory_path)
