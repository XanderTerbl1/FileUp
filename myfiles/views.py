from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

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

            response_data = {
                "message": 'HAHA! IT WORKED WANKER. RETURN DETAILS ABOUT IT HERE.'
            }

            return JsonResponse(response_data)
        else:
            # TODO - Replace with json response
            # Not a POST request
            return redirect('myfiles')
    else:
        # TODO - Replace with json response
        # Not Authenticated
        return redirect('myfiles')
