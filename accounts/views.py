from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from django.core import serializers
from django.http import JsonResponse
from .models import UserPreferences
import json

# django user model
from django.contrib.auth.models import User
from myfiles.models import Folder, File
from .models import UserPreferences


@login_required(login_url='/accounts/login')
def dashboard(request):
    user_id = request.user.id
    user_preferences = get_object_or_404(UserPreferences,  user=user_id)
    folder_count = len(
        list(Folder.objects.all().filter(owner_id=user_id).values("id"))) - 1
    file_count = len(
        list(File.objects.all().filter(owner_id=user_id).values("id")))
    perc_used = round((user_preferences.current_usage_mb /
                       user_preferences.max_usage_mb)*100, 2)

    context = {
        'folder_count': folder_count,
        'file_count': file_count,
        'user_preferences': user_preferences,
        'percentage_used': perc_used,
    }

    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='/accounts/login')
def save_preferences(request):
    if (request.method == 'POST'):
        cur_user = request.user
        info = get_object_or_404(UserPreferences, user=cur_user)
        if (request.POST['recycle_lifetime']):
            info.recyclebin_lifetime = request.POST['recycle_lifetime']
        if (request.POST['first_name']):
            cur_user.first_name = request.POST['first_name']
        if (request.POST['last_name']):
            cur_user.last_name = request.POST['last_name']

        info.save()
        cur_user.save()
        messages.success(request, "User Info updated.")
        return redirect('dashboard')


@login_required(login_url='/accounts/login')
def quota_info(request):
    """
    Returns user quota info as JSON
    """
    user = get_object_or_404(User, id=request.user.id)
    quota, created = UserPreferences.objects.get_or_create(user=user)

    ser_quota = serializers.serialize('json', [quota, ])
    dict_quota = json.loads(ser_quota)

    resp = {
        'quota': dict_quota[0]['fields']
    }

    return JsonResponse(resp)


@login_required(login_url='/accounts/login')
def users_all(request):
    """
    Returns name + surname and email of all users
    """
    user_id = request.user.id
    users = User.objects.exclude(id=user_id).values(
        "id", "first_name", "last_name", "email")

    return JsonResponse({"users": list(users)})


# TODO Implement...
@login_required(login_url='/accounts/login')
def groups_all(request):
    """
    Returns all group names and their ids
    """

    return JsonResponse({"msg": "noice"})


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        email = request.POST['email']
        username = email

        password = request.POST['password']
        password2 = request.POST['password2']

        # Validate Fields
        if (password != password2):
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if (User.objects.filter(username=username).exists()):
            messages.error(request, "Email is already taken")
            return redirect('register')

        user = User.objects.create_user(
            username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        user.save()

        userpref, created = UserPreferences.objects.get_or_create(user=user)

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
