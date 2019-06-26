from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


"""
Bit of redundant fields between Folder & File is better
than dealing with the problems with multi-tables or inheritance. x_X
"""


class DirectoryItem(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # a parent folder of null/blank would indicate a root folder.
    # A users root folder is created upon registration

    date_created = models.DateTimeField(default=datetime.now)
    is_recycled = models.BooleanField(default=False)

    # auto updates on changes. Recycled will be last change.
    # it's a workaround - better than making custom save function
    date_recycled = models.DateTimeField(auto_now=True)

    is_public = models.BooleanField(default=False)
    is_shared = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Folder(DirectoryItem):
    parent_folder = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class File(DirectoryItem):
    parent_folder = models.ForeignKey(Folder, on_delete=models.CASCADE)

    file_source = models.FileField(upload_to='uploads/%Y/%m/%d/')
    file_type = models.CharField(max_length=20)

    def __str__(self):
        return self.name
