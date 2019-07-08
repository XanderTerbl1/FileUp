from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.models import User, Group
from django.core import serializers
from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from decimal import Decimal
import json
import os

from .models import Folder, File
from shared.models import SharedFolder, SharedFile
from shared.views import confirmSharedParent
from accounts.models import UserPreferences
from public.views import confirmPublicParent
from fileup.mailer import email_groups, email_users


def confirmUserOwnedParent(requested_obj, user_id):
    """
    Confirms recursiveley that a file is (or is a descendant of) a user owned folder
    and that the user has access to it.
    """
    if (requested_obj.owner.id == user_id):
        return True

    parent = requested_obj.parent_folder
    while (parent):
        if (parent.owner.id == user_id):
            return True
        parent = parent.parent_folder
    return False


def getLiableOwner(directory_item):
    """
    Fetches the owner liable for the file directory_item.
    Recall - OWNERS of shared folders are charged for the entire shared folder

    People uploading to the shared folder will not be charged
    """
    parent = directory_item
    while (parent.parent_folder):
        parent = parent.parent_folder

    return parent.owner


def confirmUserAccess(requested_obj, user_id):
    """
    Is the user allowed to access the requested file.

    It could be his file or it could be that the file ('s parent)
    was shared with him
    """
    # Is it the user's file?
    if (requested_obj.owner.id != user_id):
        # Does he own the root/some parent folder?
        if (not confirmUserOwnedParent(requested_obj, user_id)):
            # Is it a file that was shared with him?
            if (not confirmSharedParent(requested_obj, user_id)[0]):
                # Then he does not have access to it
                return False
    return True


@login_required(login_url='/accounts/login')
def myfiles(request):
    """
    Serves current user his root folder and files.
    root folders are defined as follow
        - folder name = username
        - owned by user id
        - parent_folder_id = null.  Only root folders can have this property
    """

    root_folder, created = Folder.objects.get_or_create(
        name=request.user.username,
        owner=request.user,
        parent_folder__isnull=True
    )

    folders = Folder.objects.filter(
        parent_folder=root_folder, is_recycled=False).order_by('name')
    files = File.objects.filter(
        parent_folder=root_folder, is_recycled=False).order_by('name')

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
    requested_folder = Folder.objects.get(id=requested_folder_id)

    # Is it the users folder?
    if (requested_folder.owner.id != cur_user_id):
        # Does he own the root/some parent folder?
        if (not confirmUserOwnedParent(requested_folder, cur_user_id)):
            # Then he does not have access to it
            raise PermissionDenied

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
        parent_folder__isnull=True
    )

    context = {
        'folders': folders,
        'files': files,
        'root': root_folder,
        'breadcrumbs': bc_trail,
        'current': requested_folder
    }

    return render(request, 'myfiles/files.html', context)


@login_required(login_url='/accounts/login')
def search(request):
    """
    Search through the USER'S files for any
    file name that contains the query
    """
    query = request.GET["query"]
    if (query == ""):
        return redirect("myfiles")

    cur_user_id = request.user.id
    folders = Folder.objects.filter(
        owner=cur_user_id, is_recycled=False, name__icontains=query, parent_folder__isnull=False).order_by('name')
    files = File.objects.filter(
        owner=cur_user_id, is_recycled=False, name__icontains=query).order_by('name')

    context = {
        'folders': folders,
        'files': files,
        'query': query,
    }

    return render(request, 'myfiles/search.html', context)


@login_required(login_url='/accounts/login')
def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST['folder_name']
        parent_folder = Folder.objects.get(
            id=request.POST['current_folder_id'])

        # the shared flag in this response
        # indicates that it is created in Shard Files
        # and should be navigated as such
        shared = True if request.POST.get('shared') else False

        # create and save the new folder
        folder = Folder(
            name=folder_name,
            owner=request.user,
            parent_folder=parent_folder
        )
        folder.save()

        # Redirect to one of the only two places users can create folders
        if (shared):
            return redirect('shared/content/view/' + str(parent_folder.id))
        else:
            return redirect('folders/' + str(parent_folder.id))


@login_required(login_url='/accounts/login')
def upload_file(request):
    """
    The only (final) entry point to upload files 
    to the server
    """
    if request.method == 'POST':
        if request.FILES.get("upload_file"):
            # Get Info about the file and its parent
            parent_folder = Folder.objects.get(
                id=request.POST['current_folder_id'])

            file_name = request.FILES.get("upload_file").name
            file_type = file_name.split(".")[-1]  # (^_^)

            file_size = Decimal(
                request.FILES['upload_file'].size / (1024 * 1024))  # to mb
            liable_owner = getLiableOwner(parent_folder)

            # Does the liable owner have enough space to store this file?
            prefs = get_object_or_404(UserPreferences, user=liable_owner)
            if (prefs.max_usage_mb - prefs.current_usage_mb > file_size):
                file = File(
                    name=file_name,
                    owner=request.user,
                    parent_folder=parent_folder,
                    file_type=file_type,
                    file_source=request.FILES['upload_file']
                )
                file.save()

                prefs.current_usage_mb += file_size
                prefs.save()
                messages.success(request, file.name + " uploaded successfully")
            else:
                # Liable user does not have enough space to store the file
                # Construct response
                addressed = "You do " if liable_owner == request.user else 'The liable user (' + \
                    liable_owner.username + ') does'
                messages.error(
                    request, addressed + ' not have enough space to store this file')

            # Redirect to one of the only two places users can upload folders from
            if (request.POST.get("shared_view")):
                return redirect('shared/content/view/' + str(parent_folder.id))
            else:
                return redirect('folders/' + str(parent_folder.id))


@login_required(login_url='/accounts/login')
def move(request, file_type):
    '''
    Move a file/folder to a different parent
    '''
    if request.method == 'POST':
        # File/Folder to be moved.
        from_id = request.POST['from_id']
        current_user_id = request.user.id

        # the folder to where it will be moved.
        to_folder = Folder.objects.get(id=request.POST['to_id'])

        # Does the user have access to the folder
        # he is trying to move it to?
        if (not confirmUserAccess(to_folder, current_user_id)):
            raise PermissionDenied

        # Give the file/folder a new parent
        if (file_type == "folder"):
            from_obj = Folder.objects.get(id=from_id)
        elif (file_type == "file"):
            from_obj = File.objects.get(id=from_id)

        if (from_obj is not None):
            from_obj.parent_folder = to_folder
            from_obj.save()

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
        current_user_id = request.user.id
        name = request.POST['name']

        if (file_type == "folder"):
            request_obj = Folder.objects.get(id=file_id)
        elif (file_type == "file"):
            request_obj = File.objects.get(id=file_id)

        if (request_obj is not None):
            # Does the user have access?
            if (not confirmUserAccess(request_obj, current_user_id)):
                raise PermissionDenied

            request_obj.name = name
            request_obj.save()

            resp = {
                "id":  file_id,
                "file_type": file_type,
                "name": name  # the new file name
            }

            return JsonResponse(resp)


@login_required(login_url='/accounts/login')
def remove(request, file_type):
    '''
    Move the file/folder to the recycle bin
    where it will stay for (user defined) days 
    before being deleted
    '''
    if request.method == 'POST':
        request_obj_id = request.POST['id']
        current_user_id = request.user.id

        if (file_type == "folder"):
            request_obj = Folder.objects.get(id=request_obj_id)
        elif (file_type == "file"):
            request_obj = File.objects.get(id=request_obj_id)

        if (request_obj is not None):
            if (not confirmUserAccess(request_obj, current_user_id)):
                raise PermissionDenied

            request_obj.is_recycled = True
            request_obj.save()

            resp = {
                "id": request_obj_id,
                "type": file_type,
                "name": request_obj.name  # provided for alert purposes
            }

            return JsonResponse(resp)


@login_required(login_url='/accounts/login')
def publish(request, file_type):
    """
    Makes folder/file public by setting the is_public = True
    It returns a full link to access the file
    as part of the json response
    """
    if request.method == 'POST':
        file_id = request.POST['id']
        owner_id = request.user.id

        # User must OWN a folder inorder to make it public
        try:
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
                    "file_type": file_type,
                    "access_link": url,
                    "rel_path": rel_path
                }

                return JsonResponse(resp)
        except:
            return JsonResponse({"msg": "You need to own a file to create a public link"}, status=406)


@login_required(login_url='/accounts/login')
def unpublish(request, file_type):
    """
    Removes the is_public field from a file
    """
    if request.method == 'POST':
        file_id = request.POST['id']
        owner_id = request.user.id

        try:
            if (file_type == "folder"):
                request_obj = Folder.objects.get(id=file_id, owner=owner_id)
            elif (file_type == "file"):
                request_obj = File.objects.get(id=file_id, owner=owner_id)

            if (request_obj is not None):

                request_obj.is_public = False
                request_obj.save()

                resp = {
                    "id": file_id,
                    "file_type": file_type
                }

                return JsonResponse(resp)
        except:
            return JsonResponse({"msg": "You need to own a file to remove a public link"}, status=406)


@login_required(login_url='/accounts/login')
def share(request):
    """
    Share a file/folder with a certain group of people
    Only the owner of a file/folder may share it
    """
    if request.method == 'POST':
        file_type = request.POST['type']
        file_id = request.POST['id']
        owner_id = request.user.id

        try:
            if (file_type == "folder"):
                request_obj = Folder.objects.get(id=file_id, owner=owner_id)
            elif (file_type == "file"):
                request_obj = File.objects.get(id=file_id, owner=owner_id)
        except Folder.DoesNotExist:
            return JsonResponse({"msg": "You can't share a folder you don't own"}, status=401)
        except File.DoesNotExist:
            return JsonResponse({"msg": "You can't share a file you don't own"}, status=401)

        if (request_obj is not None):
            if (request.POST.get("user_ids[]") or request.POST.get("group_ids[]")):
                request_obj.is_shared = True
            else:
                request_obj.is_shared = False
            request_obj.save()

            if (file_type == "folder"):
                shared, created = SharedFolder.objects.get_or_create(
                    folder=request_obj
                )
            else:
                shared, created = SharedFile.objects.get_or_create(
                    file=request_obj
                )

            existing_users_dict = list(shared.users.all().values('id'))
            existing_groups_dict = list(shared.groups.all().values('id'))

            # Convert the dict[] to single value list
            existing_users = []
            existing_groups = []

            for user_dict in existing_users_dict:
                existing_users.append(user_dict['id'])

            for group_dict in existing_groups_dict:
                existing_groups.append(group_dict['id'])
            # -----------------------------------------

            new_users = []
            new_groups = []

            if (not created):
                shared.users.clear()
                shared.groups.clear()

            for id in request.POST.getlist("user_ids[]"):
                shared.users.add(id)
                if (id not in existing_users):
                    new_users.append(id)

            for name in request.POST.getlist("group_ids[]"):
                group = Group.objects.get(name=name)
                shared.groups.add(group)
                if (group.id not in existing_groups):
                    new_groups.append(group.id)

            shared.save()

            subject = 'FileUP | ' + request.user.first_name + \
                " shared a " + file_type + " with you"
            body = "'" + request_obj.name + \
                "(" + file_type + ")'   " + \
                " has been shared with you. You can view it here: " +\
                request.META['HTTP_HOST'] + "/shared"

            # Send emails to all the new users/groups of the shared file
            email_groups(new_groups, request.user.email,  subject, body)
            email_users(new_users, request.user.email,  subject, body)

            resp = {
                "id": request_obj.id,
                "type": file_type,
                'email_groups': new_groups,
                'email_users': new_users
            }

            return JsonResponse(resp)


def download(request, file_id):
    file_obj = File.objects.get(id=file_id)
    if (request.user.is_authenticated):
        if (not confirmUserAccess(file_obj, request.user.id)):
            raise PermissionDenied
    elif (not confirmPublicParent(file_obj)[0]):
        raise PermissionDenied

    file_path = file_obj.file_source.url[1:]
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(
                fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'inline; filename=' + \
                file_obj.name
            return response
    else:
        raise Http404
