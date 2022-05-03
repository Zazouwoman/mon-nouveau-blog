
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path as url
from . import views

#This will import our view that we have already created

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('success/', views.successView, name='success'),
    path('application/pdf', views.InfoEmailView.as_view()),
] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
        #urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)