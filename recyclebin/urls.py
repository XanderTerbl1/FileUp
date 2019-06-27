from django.urls import path
from . import views

urlpatterns = [
    path('', views.recylebin, name='recyclebin'),
    path('restore/<str:file_type>', views.restore, name='restore'),
    path('perm_delete/<str:file_type>', views.perm_delete, name='perm_delete'),
]
