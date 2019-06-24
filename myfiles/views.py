from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.models import User
from django.core import serializers
from datetime import datetime
from django.contrib import messages
import json
import os
from django.http import Http404

from .models import Folder, File
from shared.models import SharedFolder
from shared.views import confirmSharedParent


def confirmUserOwnedParent(requested_obj, user_id):
    """
    This function checks if the users owns any parent folders up the tree

    When a file/folder is requested that is not the user's via this app
    it could be that he owns the root folder.
    Meaning he shared the original folder - and content was added within
    """
    if (requested_obj.owner.id == user_id):
        return True

    parent = requested_obj.parent_folder
    while (parent):
        if (parent.owner.id == user_id):
            return True
        parent = parent.parent_folder
    return False


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
    # Used to simulate slow server
    # sleep(2.5)
    root_folder, created = Folder.objects.get_or_create(
        name=request.user.username,
        owner=request.user,
        parent_folder__isnull=True
    )

    # root_folder = Folder.objects.get(
    # )

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
def search(request):
    query = request.GET["query"]
    print(query)
    if (query == ""):
        return redirect("myfiles")

    cur_user_id = request.user.id
    folders = Folder.objects.filter(
        owner=cur_user_id, is_recycled=False, name__icontains=query).order_by('name')
    files = File.objects.filter(
        owner=cur_user_id, is_recycled=False, name__icontains=query).order_by('name')

    context = {
        'folders': folders,
        'files': files,
        'query': query,
    }

    return render(request, 'myfiles/search.html', context)


@login_required(login_url='/accounts/login')
def folders(request, folder_id):
    requested_folder_id = folder_id
    cur_user_id = request.user.id

    # check if the current user
    # owns the folder you are trying to show here.
    # if he doesn't we should throw unauthorized

    # Used to simulate slow server
    # sleep(2.5)

    requested_folder = Folder.objects.get(id=requested_folder_id)
    # Is it the users folder?
    if (requested_folder.owner.id != cur_user_id):
        # Does he own the root/some parent folder?
        if (not confirmUserOwnedParent(requested_folder, cur_user_id)):
            # Then he does not have access to it
            print("User does not have access")
            raise Http404

    # get all the children of the current_folder
    folders = Folder.objects.filter(
        parent_folder=requested_folder_id, is_recycled=False).order_by('name')

    files = File.objects.filter(
        parent_folder=requested_folder_id, is_recycled=False).order_by('name')

    # breadcrumb trail
    bc_trail = []
    parent = requested_folder.parent_folder
    while (parent):
        bc_trail.insert(0, parent)
        parent = parent.parent_folder

    root_folder = Folder.objects.get(
        name=request.user.username,
        owner=request.user,
        parent_folder__isnull=True)
    # The folder/files that need to be served - along with info
    # about the current folder(in this case the root)
    context = {
        'folders': folders,
        'files': files,
        'root': root_folder,
        'breadcrumbs': bc_trail,
        'current': requested_folder
    }

    return render(request, 'myfiles/files.html', context)


@login_required(login_url='/accounts/login')
def create_folder(request):
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
            messages.success(request, file.name + " uploaded successfully")
            if (request.POST.get("shared_view")):
                return redirect('shared/content/view/' + str(parent_folder.id))
            else:
                return redirect('folders/' + str(parent_folder.id))


@login_required(login_url='/accounts/login')
def move(request, file_type):
    '''
    Currently - inorder to move a file/folder into a folder
    you need to own the to and from files
    Will be updated if needed when doing the sharing app
    '''
    if request.method == 'POST':
        # File/Folder to be moved.
        from_id = request.POST['from_id']
        owner_id = request.user.id

        # the folder to where it will be moved.
        to_folder = Folder.objects.get(
            id=request.POST['to_id'], owner=owner_id)

        if (file_type == "folder"):
            from_obj = Folder.objects.get(id=from_id, owner=owner_id)
            from_obj.parent_folder = to_folder
            from_obj.save()

        elif (file_type == "file"):
            from_obj = File.objects.get(id=from_id, owner=owner_id)
            from_obj.parent_folder = to_folder
            from_obj.save()

        if (from_obj is not None):
            resp = {
                "type": file_type,
                "from_id":  from_id,
                "to_id": request.POST["to_id"],
                "from_name": from_obj.name,
                "to_name": to_folder.name
            }

            return JsonResponse(resp)


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
    '''
    Move the file/folder to the recycle bin 
    where it will stay x ammount of time 
    before being deleted

    tags: DELETE/REMOVE/MOVE TO RECYCLE BIN
    '''
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
            rel_path = '/public/' + file_type + "/" + str(file_id)
            url = request.META['HTTP_HOST'] + rel_path
            request_obj.is_public = True
            request_obj.save()

            resp = {
                "id": file_id,
                "access_link": url,
                "rel_path": rel_path
            }

            return JsonResponse(resp)


@login_required(login_url='/accounts/login')
def share(request):
    """
    """
    if request.method == 'POST':
        file_id = request.POST['id']
        owner_id = request.user.id
        if (request.POST['type'] == "folder"):
            request_obj = Folder.objects.get(id=file_id, owner=owner_id)
        elif (request.POST['type'] == "file"):
            request_obj = File.objects.get(id=file_id, owner=owner_id)

        if (request_obj is not None):
            if (request.POST.get("user_ids")):
                request_obj.is_shared = True
            else:
                request_obj.is_shared = False

            # Sharing files works up to here.
            # SharedFolder is only folder...
            # Need to make SharedFile
            request_obj.save()
            shared, created = SharedFolder.objects.get_or_create(
                folder=request_obj
            )

            if (not created):
                shared.users.clear()

            for id in request.POST["user_ids"]:
                shared.users.add(id)

            shared.save()
            return JsonResponse({"id": "CREATED"})


def download(request, file_id):
    '''
    Currently we are serving the user the contents of the file
    inside his browser.

    This was easier/faster than making protected links. This way works
    We are just relying on the mime type to always work...
    '''

    # check if the user has access to this file
    # doesnt have to be the owner if the file is public
    # or shared
    file_obj = File.objects.get(id=file_id)
    file_path = file_obj.file_source.url[1:]
    print(file_path)
    if os.path.exists(file_path):
        print("True")
        with open(file_path, 'rb') as fh:
            response = HttpResponse(
                fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'inline; filename=' + \
                os.path.basename(file_path)
            return response
    print("wtf")
    raise Http404
