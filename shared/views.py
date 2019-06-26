from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import SharedFolder, SharedFile
from myfiles.models import Folder, File
from django.http import JsonResponse


def confirmSharedParent(requested_obj, user_id):
    '''
    Basically, if a file needs to be a descendant of a shared file
    or needs to be a shared file itself inorder to be displayed here.
    This recursiveley confirms that the file/folder or one if its parent
    are shared with this user.

    Attempts to return breadcrumb as well
    '''
    if (requested_obj.is_shared):
        if (isinstance(requested_obj, File)):
            if (SharedFile.objects.filter(users=user_id, file=requested_obj)):
                return (True, [])
        else:
            if (SharedFolder.objects.filter(users=user_id, folder=requested_obj)):
                return (True, [])

    parent = requested_obj.parent_folder
    breadcrumb = []
    while (parent):
        breadcrumb.insert(0, parent)
        if (parent.is_shared):
            if (SharedFolder.objects.filter(users=user_id, folder=parent)):
                return (True, breadcrumb)
        parent = parent.parent_folder
    return (False, [])


@login_required(login_url='/accounts/login')
def shared(request):
    """
    The root for all shared folders with this user.
    For now - it only displays all the folders shared with him
    (Not the files he shared)

    To Add
    [X] Shared With Me Files
    [ ] Files I Shared
    [ ] Shared via group
    """

    folders = Folder.objects.filter(sharedfolder__in=SharedFolder.objects.filter(
        users=request.user.id))
    files = File.objects.filter(sharedfile__in=SharedFile.objects.filter(
        users=request.user.id))

    context = {
        'folders': folders,
        'files': files
    }

    return render(request, 'shared/shared.html', context)


@login_required(login_url='/accounts/login')
def shared_content(request, folder_id):
    requested_folder = get_object_or_404(Folder, pk=folder_id)
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
        raise Http404


@login_required(login_url='/accounts/login')
def participants(request, file_id):
    '''
    Returns a list of Users and Groups that a 
    certain file/folder is shared with 
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
            return JsonResponse({"users": []})
        except SharedFile.DoesNotExist:
            return JsonResponse({"users": []})

        if (owner_id != request.user.id):
            if (not shared.users.all().filter(id=request.user.id)):
                # User does not have access to this info
                raise Http404

        return JsonResponse({"users": list(shared.users.all().values("id", "first_name", "last_name", "email"))})
