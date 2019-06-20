from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from django.core import serializers
from django.http import JsonResponse
import json

# django user model
from django.contrib.auth.models import User
from myfiles.models import Folder
from .models import UserQuota


@login_required(login_url='/accounts/login')
def info(request):
    """
    Returns info about current user as JsonResponse
    """
    user_id = request.user.id

    # Add different types of info
    # i.e. number of folders
    # i.e. number of files
    # Dashboard stuff

    quota = get_object_or_404(UserQuota,  user=user_id)
    # Convert the model to a dictionary (to pass as Json)
    ser_quota = serializers.serialize('json', [quota, ])
    dict_quota = json.loads(ser_quota)

    return JsonResponse({"quota": dict_quota[0]['fields']})


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        email = request.POST['email']
        username = email

        password = request.POST['password']
        password2 = request.POST['password2']

        # Validate Fields
        # if (password != password2):
        #     messages.error(request, "Passwords do not match")
        #     return redirect('register')

        # if (User.objects.filter(username=username).exists()):
        #     messages.error(request, "Username is already taken")
        #     return redirect('register')

        # if (User.objects.filter(email=email).exists()):
        #     messages.error(request, "Email is already taken")
        #     return redirect('register')

        user = User.objects.create_user(
            username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        user.save()

        # Create the user's root-folder
        root_folder = Folder(name=username, owner_id=user.id)
        root_folder.save()

        # auto login
        auth.login(request, user)
        return redirect("myfiles")
    else:
        return render(request, 'accounts/register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if (user is not None):
            auth.login(request, user)
            messages.success(request, 'Welcome back, ' + user.first_name)
            return redirect('myfiles')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'accounts/login.html')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('login')
