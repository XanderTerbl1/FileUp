from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core import serializers
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
        parent_folder_id=root_folder.id, owner_id=cur_user_id)
    files = File.objects.filter(
        parent_folder_id=root_folder.id, owner_id=cur_user_id)

    # The folder/files that need to be served - along with info
    # about the current folder(in this case the root)
    context = {
        'folders': folders,
        'files': files,
        'current': root_folder
    }

    # may change the path later as I feel relevant
    return render(request, 'myfiles/files.html', context)


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

            # [0] gets rid of the array wrapper
            return JsonResponse(struct[0]['fields'])
        else:
            # TODO - Replace with json response
            # Not a POST request
            return redirect('myfiles')
    else:
        # TODO - Replace with json response
        # Not Authenticated
        return redirect('myfiles')


@login_required(login_url='/accounts/login')
def upload_file(request):
    if request.method == 'POST':
        parent_id = request.POST['current_folder_id']
        owner_id = request.user.id

        if request.FILES.get("upload_file"):
            # Save the file
            file_name = request.FILES.get("upload_file").name
            file_type = file_name.split(".")[-1]#  (^_^)
            file = File(
                name=file_name,
                owner_id=owner_id,
                parent_folder_id=parent_id,
                file_type = file_type,
                file_source=request.FILES['upload_file']
            )
            file.save()

            # TODO - redirect to where they came from
            return redirect('myfiles')
