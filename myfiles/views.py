from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core import serializers
from datetime import datetime
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

    cur_user_id = request.user.id
    root_folder = Folder.objects.get(
        name=request.user.username,
        owner_id=cur_user_id,
        parent_folder_id__isnull=True)

    folders = Folder.objects.filter(
        parent_folder_id=root_folder.id, owner_id=cur_user_id, is_recycled=False).order_by('name')
    files = File.objects.filter(
        parent_folder_id=root_folder.id, owner_id=cur_user_id).order_by('name')

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
        Folder, pk=requested_folder_id, owner_id=cur_user_id)

    # get all the children of the current_folder
    folders = Folder.objects.filter(
        parent_folder_id=requested_folder_id, owner_id=cur_user_id, is_recycled=False).order_by('name')

    files = File.objects.filter(
        parent_folder_id=requested_folder_id, owner_id=cur_user_id).order_by('name')

    # The folder/files that need to be served - along with info
    # about the current folder(in this case the root)
    context = {
        'folders': folders,
        'files': files,
        'current': requested_folder
    }

    return render(request, 'myfiles/files.html', context)


@login_required(login_url='/accounts/login')
def create_folder(request):
    if (request.user.is_authenticated):
        if request.method == 'POST':
            folder_name = request.POST['folder_name']
            parent_id = request.POST['current_folder_id']
            owner_id = request.user.id

            # create and save the new folder
            folder = Folder(
                name=folder_name,
                owner_id=owner_id,
                parent_folder_id=parent_id
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
def delete_folder(request):
    if request.method == 'POST':
        folder_id = request.POST['folder_id']
        owner_id = request.user.id

        # TODO - Throw 401 instead of 404
        requested_folder = get_object_or_404(
            Folder, pk=folder_id, owner_id=owner_id)

        # Move requested folder to recycle bin
        requested_folder.update(
            is_recycled=True, date_recycled=datetime.now)

        return JsonResponse({"id": folder_id})


@login_required(login_url='/accounts/login')
def upload_file(request):
    if request.method == 'POST':
        if request.FILES.get("upload_file"):
            # Save the file
            parent_id = request.POST['current_folder_id']
            owner_id = request.user.id
            # current_folder = Folder.objects.get(id = parent_id)

            file_name = request.FILES.get("upload_file").name
            file_type = file_name.split(".")[-1]  # (^_^)

            file = File(
                name=file_name,
                owner_id=owner_id,
                parent_folder_id=parent_id,
                file_type=file_type,
                file_source=request.FILES['upload_file']
            )
            file.save()

            # TODO - redirect to where they came from
            return redirect('folders/' + parent_id)


@login_required(login_url='/accounts/login')
def rename_folder(request):
    if (request.user.is_authenticated):
        if request.method == 'POST':
            file_id = request.POST['id']

            # TODO - Make sure that the user owns this file
            # Or that he can added it
            #confirmPermissions(id=file_id, perm=write ,type=file)

            name = request.POST['name']
            owner_id = request.user.id

            # check if it is a file/folder
            # for now assuming folder

            folder = Folder.objects.filter(id=file_id).update(name=name)
            print(folder)
            return JsonResponse({"id":  file_id, "name": name})
