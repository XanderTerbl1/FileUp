from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.models import User, Group
from django.core import serializers
from datetime import datetime
from django.contrib import messages
import json
import os
from django.http import Http404
from .models import Folder, File
from shared.models import SharedFolder, SharedFile
from shared.views import confirmSharedParent
from accounts.models import UserPreferences
from decimal import Decimal
from public.views import confirmPublicParent


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


def getLiableOwner(directory_item):
    """
    Fetches the owner that ought to be charged for the file
    just uploaded.
    Recall - OWNERS of shared folders are charged for the entire shared folder     
    """
    # Check who owns the highest parent
    parent = directory_item
    while (parent.parent_folder):
        parent = parent.parent_folder

    return parent.owner


def confirmUserAccess(requested_obj, user_id):
     # Is it the user's file?
    if (requested_obj.owner.id != user_id):
        print("Failed 1")
        # Does he own the root/some parent folder?
        if (not confirmUserOwnedParent(requested_obj, user_id)):
            print("Failed 2")
            # Is it a file that was shared with him?
            if (not confirmSharedParent(requested_obj, user_id)[0]):
                print("Failed 3")
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
def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST['folder_name']
        parent_folder = Folder.objects.get(
            id=request.POST['current_folder_id'])

        shared = True if request.POST.get('shared') else False
        print(shared)

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

        resp = {
            "folder": struct[0],
            "shared": shared
        }
        return JsonResponse(resp)


@login_required(login_url='/accounts/login')
def upload_file(request):
    if request.method == 'POST':
        if request.FILES.get("upload_file"):
            # Save the file
            parent_folder = Folder.objects.get(
                id=request.POST['current_folder_id'])

            file_name = request.FILES.get("upload_file").name
            file_type = file_name.split(".")[-1]  # (^_^)

            file_size = Decimal(
                request.FILES['upload_file'].size / 1000000)  # to mb
            liable_owner = getLiableOwner(parent_folder)

            # Is there enough space?
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
                addressed = "You do " if liable_owner == request.user else 'The liable user (' + \
                    liable_owner.username + ') does'

                messages.error(
                    request, addressed + ' not have enough space to store this file')

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
        current_user_id = request.user.id

        # the folder to where it will be moved.
        to_folder = Folder.objects.get(id=request.POST['to_id'])

        # Does the user have access to the folder
        # he is trying to move it to?
        if (not confirmUserAccess(to_folder, current_user_id)):
            print("User does not have access")
            raise Http404

        if (file_type == "folder"):
            from_obj = Folder.objects.get(id=from_id)
        elif (file_type == "file"):
            from_obj = File.objects.get(id=from_id)

        # # Does the owner have access to the folder
        # # that it is being moved to?
        # # (Can't deny an owner access to his file)
        # if (not confirmUserAccess(to_folder, from_obj.owner.id)):
        #     print("")
        #     return JsonResponse({"msg": "Can't move object out of owner's reach"}, status=406)
        # Owner of the shared folder can do any operations with the files in the shared folder.

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
                print("User does not have access")
                raise Http404

            request_obj.name = name
            request_obj.save()
            return JsonResponse({"id":  file_id, "name": name})


@login_required(login_url='/accounts/login')
def remove(request, file_type):
    '''
    Move the file/folder to the recycle bin
    where it will stay x ammount of time
    before being deleted

    When a user deletes a file that didnt originally
    belong to him - it will be deleted perm directly

    tags: DELETE/REMOVE/MOVE TO RECYCLE BIN
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
                print("User does not have access")
                raise Http404

            if (request_obj.owner.id != current_user_id):
                # deleting someone elses stuff..
                # Decide what to do when someone - that may delete
                # A folder that is not their's - delete it.
                # Whos recycle bin? Or no recycle bin?
                # I say no recycle bin
                # TODO
                pass

            request_obj.is_recycled = True
            request_obj.save()

            return JsonResponse({"id": request_obj_id, 'name': request_obj.name})


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
        file_type = request.POST['type']
        file_id = request.POST['id']
        owner_id = request.user.id
        if (file_type == "folder"):
            request_obj = Folder.objects.get(id=file_id, owner=owner_id)
        elif (file_type == "file"):
            request_obj = File.objects.get(id=file_id, owner=owner_id)

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

            if (not created):
                shared.users.clear()
                shared.groups.clear()

            for id in request.POST.getlist("user_ids[]"):
                shared.users.add(id)

            for name in request.POST.getlist("group_ids[]"):
                group = Group.objects.get(name=name) 
                shared.groups.add(group)

            shared.save()
            return JsonResponse({"id": "CREATED"})


def download(request, file_id):
    '''    
    '''
    file_obj = File.objects.get(id=file_id)
    if (request.user.is_authenticated):
        if (not confirmUserAccess(file_obj, request.user.id)):
            raise Http404
    elif (not confirmPublicParent(file_obj)):
        raise Http404

    file_path = file_obj.file_source.url[1:]
    if os.path.exists(file_path):
        print("True")
        with open(file_path, 'rb') as fh:
            response = HttpResponse(
                fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'inline; filename=' + \
                os.path.basename(file_path)
            return response

    raise Http404
