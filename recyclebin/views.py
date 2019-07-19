from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from datetime import datetime, timedelta

from myfiles.models import File, Folder
from myfiles.views import getLiableOwner
from accounts.models import UserPreferences


@login_required(login_url='/accounts/login')
def recylebin(request):
    """
    Serves current user all his recycled folders and files\n
    # Files in recycle bin still accounts for storage of liable user.\n
    # Recycled folders cant be traversed.\n
    # File Hierarchy wont be kept in recycle bin (i.e. all deleted items are same level).\n
    """
    autoRecyle(request.user.id)

    cur_user_id = request.user.id

    folders = Folder.objects.filter(
        owner_id=cur_user_id, is_recycled=True).order_by('name')
    files = File.objects.filter(
        owner_id=cur_user_id, is_recycled=True).order_by('name')

    context = {
        'folders': folders,
        'files': files,
    }

    return render(request, 'recyclebin/bin.html', context)


@login_required(login_url='/accounts/login')
def restore(request, file_type):
    """
    Restore the file/folder to its original parent\n
    If file_type == 'all', all files/folders will be restored.
    """
    if request.method == 'POST':
        owner_id = request.user.id
        # Restore All Files and Folders
        if (file_type == "all"):
            Folder.objects.filter(owner_id=owner_id,
                                  is_recycled=True).update(is_recycled=False)
            File.objects.filter(owner_id=owner_id,
                                is_recycled=True).update(is_recycled=False)
            return redirect('recyclebin')
        else:
            # Restore selected file/folder
            file_id = request.POST['id']
            if (file_type == "folder"):
                request_obj = Folder.objects.get(id=file_id, owner=owner_id)
            elif (file_type == "file"):
                request_obj = File.objects.get(id=file_id, owner=owner_id)

            if (request_obj is not None):
                request_obj.is_recycled = False
                request_obj.save()
                return JsonResponse({"id": file_id})


@login_required(login_url='/accounts/login')
def perm_delete(request, file_type):
    """
    Permanently deletes the file/folder(recursively).

    We do not count on CASCADE deleting - since we want
    to determine which users needs to be 'compensated'
    with storage with each delete (It isn't necessarily 
    the user that makes the request: consider shared folders - 
    the owner of the folder carries all cost )
    """
    if request.method == 'POST':
        file_id = request.POST['id']
        owner_id = request.user.id

        if file_type == 'folder':
            # Permanently delete this folder and all its children
            root = Folder.objects.get(id=file_id, owner=owner_id)
            total_deleted = delete_recursvie(root)

            resp = {
                "id": file_id,
                "total_deleted": total_deleted
            }

            return JsonResponse(resp)

        elif file_type == "file":
            # Permanently delete this file
            f = File.objects.get(id=file_id, owner=owner_id)
            owner = getLiableOwner(f)

            size = f.file_source.size / (1024 * 1024)
            compensateLiableOwner(owner, [size, ])

            f.file_source.delete()  # delete from server
            f.delete()

            resp = {
                "id": file_id,
                "total_deleted": 1
            }

            return JsonResponse(resp)


def delete_recursvie(folder):
    total_deleted = 0
    folders = Folder.objects.filter(parent_folder=folder)

    for f in folders:
        total_deleted += delete_recursvie(f)

    files = File.objects.filter(parent_folder=folder)
    # Calculate the storage that the liable user must be compensated with
    sizes = []

    for f in files:
        sizes.append((f.file_source.size / 1024 * 1024))
        f.file_source.delete()  # delete from the server

    owner = getLiableOwner(folder)
    compensateLiableOwner(owner, sizes)

    count = files.delete()  # delete from DB
    total_deleted += count[0]

    folder.delete()  # delete from DB
    return (total_deleted + 1)


def compensateLiableOwner(owner, sizes):
    total = Decimal(sum(sizes))
    userprefs = UserPreferences.objects.get(user=owner)
    if (userprefs.current_usage_mb - total < 0):
        userprefs.current_usage_mb = 0
    else:
        userprefs.current_usage_mb -= total
    userprefs.save()


def autoRecyle(user_id):
    """
    This function gets all the files/folders in the recycle bin (for a single user) that 
    passed its 'expired' date (as specified by user) and deletes them 

    It is most likely called when the users requests his recyclebin

    Future updates will call this function for ALL users automatically (using task scheduler)
    """
    user_prefs = UserPreferences.objects.get(user=user_id)
    recycle_lifetime = user_prefs.recyclebin_lifetime

    time_threshold = datetime.now() - timedelta(days=recycle_lifetime)
    folders = Folder.objects.filter(
        owner_id=user_id, is_recycled=True, date_recycled__lt=time_threshold)
    files = File.objects.filter(
        owner_id=user_id, is_recycled=True, date_recycled__lt=time_threshold)

    for _folder in folders:
        delete_recursvie(_folder)

    for _file in files:
        owner = getLiableOwner(_file)

        size = _file.file_source.size / (1024 * 1024)
        compensateLiableOwner(owner, [size, ])

        _file.file_source.delete()
        _file.delete()
