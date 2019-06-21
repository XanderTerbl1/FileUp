from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('myfiles.urls')),
    path('accounts/', include('accounts.urls')),
    path('recyclebin/', include('recyclebin.urls')),
    path('public/', include('public.urls')),
    path('shared/', include('shared.urls')),
    path('admin/', admin.site.urls),
]
# This will allow files to be accessed if they have the url
# we do not want that...
# + static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
