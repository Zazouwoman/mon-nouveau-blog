
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
	path('pdf/facture/<int:id>/',views.facture_pdf,name="facture_pdf"),
    path('pdf/attachment/<int:id>/',views.attachment_pdf,name="attachment_pdf"),
    path('word/relance2/<int:id>/',views.relance_word2,name="relance_word2"),
    path('word/relance2bis/<int:id>/',views.relance_word2bis,name="relance_word2bis"),
    path('pdf/relance2/<int:id>/',views.relance_pdf2,name="relance_pdf2"),
    path('word/relance3/<int:id>/',views.relance_word3,name="relance_word3"),
    path('word/relance3bis/<int:id>/', views.relance_word3bis, name="relance_word3bis"),
    path('pdf/relance3/<int:id>/', views.relance_pdf3, name="relance_pdf3"),
    path('word/relance4/<int:id>/',views.relance_word4,name="relance_word4"),
    path('word/relance4bis/<int:id>/', views.relance_word4bis, name="relance_word4bis"),
    path('pdf/relance4/<int:id>/', views.relance_pdf4, name="relance_pdf4"),
    path('lien/fichier_word2/<int:id>/', views.lien_fichier_word2, name="lien_fichier_word2"),
    path('lien/fichier_word3/<int:id>/', views.lien_fichier_word3, name="lien_fichier_word3"),
    path('lien/fichier_word4/<int:id>/', views.lien_fichier_word4, name="lien_fichier_word4"),
] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
