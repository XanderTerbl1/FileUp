from django.urls import path

from . import views

#i.e. public/folder/101
urlpatterns = [
    path('<str:file_type>/<int:file_id>', views.public, name='public'),
]
