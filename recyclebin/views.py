from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from myfiles.models import File, Folder


@login_required(login_url='/accounts/login')
def recylebin(request):
    """
    Serves current user all his recycled folders and files.
    # Recycled folders has to be restored in order to traverse them.
    # File Hierarchy wont be kept in recycle bin (i.e. all deleted items are same level)       
    """
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
    if request.method == 'POST':
        file_id = request.POST['id']
        owner_id = request.user.id

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
    Permanently deletes the file/folder (recursively).
    All the children of said folder will also be deleted.
    """
    if request.method == 'POST':
        file_id = request.POST['id']
        owner_id = request.user.id

        if file_type == 'folder':
            root = Folder.objects.get(id=file_id, owner=owner_id)
            total_deleted = delete_recursvie(root, owner_id)
            return JsonResponse({"id": file_id, "total_deleted": total_deleted})
        elif file_type == "file":
            files = File.objects.filter(
                id=file_id, owner=owner_id).delete()
            return JsonResponse({"id": file_id, "total_deleted": 1})


def delete_recursvie(folder, owner_id):
    total_deleted = 0
    folders = Folder.objects.filter(parent_folder=folder, owner=owner_id)

    for f in folders:
        total_deleted += delete_recursvie(f, owner_id)

    # Delete the files within in the folder as well
    # TODO - Delete the files from the server as well!
    # TODO - Count the numbers of files we deleted as well!
    files = File.objects.filter(parent_folder=folder, owner=owner_id).delete()
    total_deleted += files[0]

    folder.delete()
    return (total_deleted + 1)
