from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import SharedFolder


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
    shared_folders = SharedFolder.objects.filter(users=request.user.id)
    print(shared_folders)

    context = {
        'shared_folders': shared_folders
    }

    return render(request, 'shared/shared.html', context)
