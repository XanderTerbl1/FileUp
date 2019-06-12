from django.contrib import admin
from .models import Folder, File


#These files should not be visible from the admin site.
#This is just for debugging purposes
class FolderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

admin.site.register(Folder, FolderAdmin)
admin.site.register(File)