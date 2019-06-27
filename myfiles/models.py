from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


class DirectoryItem(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # a parent folder of null/blank would indicate a root folder.
    # A users root folder is created upon registration
    date_created = models.DateTimeField(default=datetime.now)
    is_recycled = models.BooleanField(default=False)

    # auto_now: updates on changes. is_recycled will be last change
    # (Improve - create custom save function)
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
