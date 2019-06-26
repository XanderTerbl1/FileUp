from django.urls import path

from . import views

# shared/*
urlpatterns = [
    path('', views.shared, name='shared'),
    path('content/view/<int:folder_id>', views.shared_content, name='shared_content'),
    path('participants/<int:file_id>', views.participants, name='participants')
]
