from django.db import models
from myfiles.models import Folder
from django.contrib.auth.models import User


class SharedFolder(models.Model):
    folder = models.OneToOneField(
        Folder, on_delete=models.DO_NOTHING)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.folder.name
