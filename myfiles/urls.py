from django.urls import path
from . import views

urlpatterns = [
    path('', views.myfiles, name='myfiles'),
    path('create_folder', views.create_folder, name='create_folder'),
    path('upload_file', views.upload_file, name='upload_file'),
]