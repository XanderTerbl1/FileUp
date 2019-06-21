from django.urls import path

from . import views

# shared/*
urlpatterns = [
    path('', views.shared, name='shared'),
]
