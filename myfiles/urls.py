from django.urls import path
from . import views

urlpatterns = [
    path('', views.myfiles, name='myfiles'),
    path('create_folder', views.create_folder, name='create_folder'),
    path('upload_file', views.upload_file, name='upload_file'),
    path('folders/<int:folder_id>', views.folders, name='folders'),
    # File Operations
    path('rename_folder', views.rename_folder, name="rename_folder"),
    path('delete_folder', views.delete_folder, name="delete_folder")    
]