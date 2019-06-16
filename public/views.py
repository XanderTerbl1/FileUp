from django.shortcuts import render, get_object_or_404
from myfiles.models import Folder, File


def public(request, file_type, file_id):
    requested_obj = get_object_or_404(
        Folder if (file_type == "folder") else File,
        pk=file_id, is_public=True)

    files = []
    folders = []
    if (file_type == "folder"):
        # kry sy kinders ook en kak
        folders = [requested_obj, ]
    elif (file_type == "file"):
        files = [requested_obj, ]

    context = {
        "folders": folders,
        "files": files
    }

    return render(request, "public/public.html", context)
