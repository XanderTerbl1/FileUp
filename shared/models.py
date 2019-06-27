from django.db import models
from myfiles.models import Folder, File
from django.contrib.auth.models import User, Group


class SharedDirectoryItem(models.Model):
    users = models.ManyToManyField(User)
    groups = models.ManyToManyField(Group)

    class Meta:
        abstract = True


class SharedFolder(SharedDirectoryItem):
    folder = models.OneToOneField(
        Folder, on_delete=models.CASCADE)

    def __str__(self):
        return self.folder.name


class SharedFile(SharedDirectoryItem):
    file = models.OneToOneField(
        File, on_delete=models.CASCADE)

    def __str__(self):
        return self.folder.name
