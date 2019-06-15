from django.urls import path
from . import views

urlpatterns = [
    path('', views.recylebin, name='recyclebin'),
    #restore/file
    #restore/folder
    path('restore/<str:file_type>', views.restore, name='restore'),
]