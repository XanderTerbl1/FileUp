from django.shortcuts import render
from django.contrib.auth.decorators import login_required


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
        owner_id=current_user_id,
        parent_folder_id__isnull=True)

    folders = Folder.objects.filter(
        parent_folder_id=root_folder.id, owner_id=current_user_id)
    files = File.objects.filter(
        parent_folder_id=root_folder.id, owner_id=current_user_id)

    #The folder/files that need to be served - along with info
    #about the current folder(in this case the root)
    context = {
        'folders': folders,
        'files' : files,
        'current' : root_folder
    }

    # may change the path later as I feel relevant
    return render(request, 'myfiles/files.html', context)
