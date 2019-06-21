from django.urls import path

from . import views

# accounts/*
urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('info', views.info, name='info'),
    path('users/all', views.users_all, name='users_all'),
    path('groups/all', views.groups_all, name='groups_all')
]
