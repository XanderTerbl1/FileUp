from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='/accounts/login')
def myfiles(request):
    return render(request, 'myfiles/files.html')#may change the path later as I feel relevant