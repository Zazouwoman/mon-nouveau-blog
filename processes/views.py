from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView, CreateView
from django.http import HttpResponse
from django.views.generic import View

from .processes import LogBackup
import os.path

# Create your views here.

@login_required
def lien_backup(request,id=None):
    backup = LogBackup.objects.get(id=id)
    nom_fichier = backup.fichier  #C'est le nom que l'on veut que le fichier ait
    fichier = backup.Fonction_Nom_Fichier()
	
    if not(os.path.exists(fichier)):
         return render(request,"bdd/facture/facture_no_fichier.html",{ "facture":backup })
		
    response = HttpResponse(content_type='application/gzip')
    response['Content-Disposition'] = 'inline; filename=%s'%nom_fichier
    with open(fichier,"rb") as f:
        response.write(f.read())
    return response

