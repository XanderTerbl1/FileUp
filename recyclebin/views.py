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
    files = File.objects.filter(owner_id=cur_user_id).order_by('name')

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
            folder = Folder.objects.get(id=file_id, owner_id=owner_id)
            folder.is_recycled = False
            folder.save()
            return JsonResponse({"id": file_id})
        elif (file_type == "file"):
            file = Folder.objects.get(id=file_id, owner_id=owner_id)
            file.is_recycled = False
            file.save()
            return JsonResponse({"id": file_id})
