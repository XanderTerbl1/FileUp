from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class Folder(models.Model):
    name = models.CharField(max_length = 200)
    owner_id = models.IntegerField()
    #a parent folder id of null/blank would indicate a root folder.
    # A users root folder is created upon registration  
    parent_folder_id = models.IntegerField(blank=True, null=True)
    date_created = models.DateTimeField(default=datetime.now, blank=True) 
