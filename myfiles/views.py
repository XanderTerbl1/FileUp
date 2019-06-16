from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.core import serializers
from datetime import datetime
from django.contrib import messages
import json

from .models import Folder, File


@login_required(login_url='/accounts/login')
def myfiles(request):
    """
    Serves current user his root folder and files.
    root folders are defined as follow
        - folder name = username
        - owned by user id
        - parent_folder_id = null.
            Only root folders can have this property
    """
    root_folder = Folder.objects.get(
        name=request.user.username,
        owner=request.user,
        parent_folder__isnull=True)

    folders = Folder.objects.filter(
        parent_folder=root_folder, owner=request.user, is_recycled=False).order_by('name')
    files = File.objects.filter(
        parent_folder=root_folder, owner=request.user, is_recycled=False).order_by('name')

    # The folder/files that need to be served - along with info
    # about the current folder(in this case the root)
    context = {
        'folders': folders,
        'files': files,
        'current': root_folder
    }

    # may change the path later as I feel relevant
    return render(request, 'myfiles/files.html', context)


@login_required(login_url='/accounts/login')
def folders(request, folder_id):
    requested_folder_id = folder_id
    cur_user_id = request.user.id

    # check if the current user
    # owns the folder you are trying to show here.
    # if he doesn't we should throw unauthorized

    # TODO - Throw 401 instead of 404
    requested_folder = get_object_or_404(
        Folder, pk=requested_folder_id, owner=cur_user_id)

    # get all the children of the current_folder
    folders = Folder.objects.filter(
        parent_folder=requested_folder_id, owner=cur_user_id, is_recycled=False).order_by('name')

    files = File.objects.filter(
        parent_folder=requested_folder_id, owner=cur_user_id, is_recycled=False).order_by('name')

    # breadcrumb trail
    bc_trail = []
    parent = requested_folder.parent_folder
    while (parent):
        bc_trail.insert(0, parent)
        parent = parent.parent_folder

    # The folder/files that need to be served - along with info
    # about the current folder(in this case the root)
    context = {
        'folders': folders,
        'files': files,
        'breadcrumbs': bc_trail,
        'current': requested_folder
    }

    return render(request, 'myfiles/files.html', context)


@login_required(login_url='/accounts/login')
def create_folder(request):
    if (request.user.is_authenticated):
        if request.method == 'POST':
            folder_name = request.POST['folder_name']
            parent_folder = Folder.objects.get(
                id=request.POST['current_folder_id'])

            # create and save the new folder
            folder = Folder(
                name=folder_name,
                owner=request.user,
                parent_folder=parent_folder
            )
            folder.save()

            # Serailize Folder
            ser_folder = serializers.serialize('json', [folder, ])

            # Convert to 'dictionary'
            struct = json.loads(ser_folder)
            print(struct)

            # [0] gets rid of the array wrapper
            return JsonResponse(struct[0])


@login_required(login_url='/accounts/login')
def upload_file(request):
    if request.method == 'POST':
        if request.FILES.get("upload_file"):
            # Save the file
            parent_folder = Folder.objects.get(
                id=request.POST['current_folder_id'])

            file_name = request.FILES.get("upload_file").name
            file_type = file_name.split(".")[-1]  # (^_^)

            file = File(
                name=file_name,
                owner=request.user,
                parent_folder=parent_folder,
                file_type=file_type,
                file_source=request.FILES['upload_file']
            )
            file.save()

            # TODO - redirect to where they came from
            return redirect('folders/' + str(parent_folder.id))


@login_required(login_url='/accounts/login')
def rename(request, file_type):
    if request.method == 'POST':
        file_id = request.POST['id']
        owner_id = request.user.id
        name = request.POST['name']

        if (file_type == "folder"):
            request_obj = Folder.objects.filter(
                id=file_id, owner=owner_id).update(name=name)
        elif (file_type == "file"):
            request_obj = File.objects.filter(
                id=file_id, owner=owner_id).update(name=name)

        if (request_obj is not None):
            return JsonResponse({"id":  file_id, "name": name})


@login_required(login_url='/accounts/login')
def remove(request, file_type):
    if request.method == 'POST':
        file_id = request.POST['id']
        owner_id = request.user.id

        if (file_type == "folder"):
            request_obj = Folder.objects.get(id=file_id, owner=owner_id)
        elif (file_type == "file"):
            request_obj = File.objects.get(id=file_id, owner=owner_id)

        if (request_obj is not None):
            request_obj.is_recycled = True
            request_obj.save()

            return JsonResponse({"id": file_id})


@login_required(login_url='/accounts/login')
def publish(request, file_type):
    """
    Makes folder/file public by setting the is_public flag
    and return a full link to access the file 
    as part of the json response
    """
    if request.method == 'POST':
        file_id = request.POST['id']
        owner_id = request.user.id

        if (file_type == "folder"):
            request_obj = Folder.objects.get(id=file_id, owner=owner_id)
        elif (file_type == "file"):
            request_obj = File.objects.get(id=file_id, owner=owner_id)

        if (request_obj is not None):
            # host/public/type/id
            url = request.META['HTTP_HOST'] + \
                '/public/' + file_type + "/" + str(file_id)
            request_obj.is_public = True
            request_obj.save()
            # TODO - Instead of sending an url
            # redirecting to public app - and adding to 'messages'
            # could also be an approach
            return JsonResponse({"id": file_id, "access_link": url})
