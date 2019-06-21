from django.db import models
from myfiles.models import Folder
from django.contrib.auth.models import User


class SharedFolder(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.DO_NOTHING)
    # The users that can access the shared folder
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.folder.name
