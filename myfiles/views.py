from django.shortcuts import render

def myfiles(request):
    return render(request, 'myfiles/files.html')#may change the path later as I feel relevant