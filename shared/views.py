from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404

from django.contrib.auth.models import User
from .models import SharedFolder, SharedFile
from myfiles.models import Folder, File


def confirmSharedParent(requested_obj, user_id):
    '''
    Confirms recursiveley that a file is (or is a descendant of) a shared file
    and that the user has access to it.

    Attempts to return a breadcrumb(trail) as well

    Returns a tuple (bool: is_shared_parent, [] : breadcrumb
    '''
    user = User.objects.get(id=user_id)
    if (requested_obj.is_shared):
        if (isinstance(requested_obj, File)):
            if (SharedFile.objects.filter(users=user_id, file=requested_obj)):
                return (True, [])
            else:
                if (SharedFile.objects.filter(groups__in=user.groups.all())):
                    return (True, [])
        else:
            if (SharedFolder.objects.filter(users=user_id, folder=requested_obj)):
                return (True, [])
            else:
                if (SharedFolder.objects.filter(groups__in=user.groups.all())):
                    return (True, [])

    parent = requested_obj.parent_folder
    breadcrumb = []
    while (parent):
        breadcrumb.insert(0, parent)
        if (parent.is_shared):
            if (SharedFolder.objects.filter(users=user_id, folder=parent)):
                return (True, breadcrumb)
            elif (SharedFolder.objects.filter(groups__in=user.groups.all())):
                return (True, breadcrumb)

        parent = parent.parent_folder

    # Missed all cases. Failed
    return (False, [])


@login_required(login_url='/accounts/login')
def shared(request):
    """
    The root for all files shared with the user

    The files that the user shared with other people, will still form
    part of their personal file directory.
    """
    # Get User & Group Shared folders
    folders = Folder.objects.filter(
        sharedfolder__in=SharedFolder.objects.filter(users=request.user.id) |
        SharedFolder.objects.filter(groups__in=request.user.groups.filter())
    )
    folders = folders.exclude(owner=request.user.id)

    # Get User & Group Shared files
    files = File.objects.filter(
        sharedfile__in=SharedFile.objects.filter(users=request.user.id) |
        SharedFile.objects.filter(groups__in=request.user.groups.filter())
    )
    files = files.exclude(owner=request.user.id)

    context = {
        'folders': folders,
        'files': files
    }

    return render(request, 'shared/shared.html', context)


@login_required(login_url='/accounts/login')
def shared_content(request, folder_id):
    requested_folder = Folder.objects.get(pk=folder_id)
    canShare, breadcrumb = confirmSharedParent(
        requested_folder, request.user.id)

    if (canShare):
        folders = Folder.objects.filter(
            parent_folder=requested_folder.id, is_recycled=False).order_by('name')

        files = File.objects.filter(
            parent_folder=requested_folder.id, is_recycled=False).order_by('name')

        context = {
            'folders': folders,
            'files': files,
            'breadcrumbs': breadcrumb,
            'current': requested_folder
        }
        return render(request, 'shared/content.html', context)
    else:
        raise PermissionDenied


@login_required(login_url='/accounts/login')
def participants(request, file_id):
    '''
    Returns a list of Users and Groups that a 
    certain file/folder is shared with.
    '''
    if request.method == 'POST':
        file_type = request.POST.get("file_type")

        try:
            if (file_type == "folder"):
                shared = SharedFolder.objects.get(
                    folder=file_id
                )
                owner_id = shared.folder.owner.id

            else:
                shared = SharedFile.objects.get(
                    file=file_id
                )
                owner_id = shared.file.owner.id

        except SharedFolder.DoesNotExist:
            return JsonResponse({"users": [], "groups": []})
        except SharedFile.DoesNotExist:
            return JsonResponse({"users": [], "groups": []})

        if (owner_id != request.user.id):
            if (not shared.users.all().filter(id=request.user.id)):
                # User does not have access to this info
                raise PermissionDenied

        users = list(shared.users.all().values("id"))
        groups = list(shared.groups.all().values('name'))

        resp = {
            'users': users,
            'groups': groups
        }

        return JsonResponse(resp)
