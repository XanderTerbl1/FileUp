from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from myfiles.models import Folder, File


def confirmPublicParent(requested_obj):
    '''
    Confirms recursiveley that a file is (or is a descendant of) a PUBLIC file
    '''
    if (requested_obj.is_public):
        return True
    else:
        parent = requested_obj.parent_folder
        while (parent):
            if (parent.is_public):
                return True
            parent = parent.parent_folder
        return False


def public(request, file_type, file_id):
    """
    This is the entry point for a public folder/file
    It serves the requested public folder 
    """
    requested_obj = get_object_or_404(
        Folder if (file_type == "folder") else File,
        pk=file_id,  is_recycled=False)

    if (confirmPublicParent(requested_obj)):
        files = []
        folders = []

        if (file_type == "folder"):
            folders = [requested_obj, ]
        elif (file_type == "file"):
            files = [requested_obj, ]

        context = {
            "folders": folders,
            "files": files
        }

        return render(request, "public/public.html", context)
    else:
        raise PermissionDenied


def public_content(request, folder_id):
    """
    Serves the content of some PUBLIC folder        
    """
    requested_folder = get_object_or_404(Folder, pk=folder_id)
    if (confirmPublicParent(requested_folder)):
        folders = Folder.objects.filter(
            parent_folder=requested_folder.id, is_recycled=False).order_by('name')

        files = File.objects.filter(
            parent_folder=requested_folder.id, is_recycled=False).order_by('name')

        context = {
            'folders': folders,
            'files': files,
            # 'root': root_folder,
            # 'breadcrumbs': bc_trail,
            'current': requested_folder
        }

        return render(request, 'public/public.html', context)
    else:
        raise PermissionDenied
