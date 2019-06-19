from django.urls import path

from . import views

#i.e. public/folder/101
#i.e. public/content/101
urlpatterns = [
    path('<str:file_type>/<int:file_id>', views.public, name='public'),
    path('content/view/<int:folder_id>',
         views.public_content, name='public_content'),
]
