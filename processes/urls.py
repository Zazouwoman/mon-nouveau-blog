
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path as url
from . import views

#This will import our view that we have already created

urlpatterns = [
	path('lien/backup/<int:id>/',views.lien_backup,name="lien_backup"),
] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
