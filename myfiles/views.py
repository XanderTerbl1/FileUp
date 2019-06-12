from django.shortcuts import render

def myfiles(request):
    return render(request, 'files.html')