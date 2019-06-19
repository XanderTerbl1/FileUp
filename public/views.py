from django.shortcuts import render, get_object_or_404
from myfiles.models import Folder, File


def confirmPublicParent(requested_obj):
    '''
    Basically, if a file needs to be a descendant of a public file
    or needs to be a public file itself inorder to be displayed here.
    This recursiveley confirms that the file/folder or one if its parent
    are public
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
    This is the root entry point
    Since there is no publicly available root folder
    for public files - we need a single file/folder view.
    This servers just that

    public_content would serve the content of a public folder
    (or descendant)
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


def public_content(request, folder_id):
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
