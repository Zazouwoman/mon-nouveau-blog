from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView, CreateView
from django.http import HttpResponse
from django.views.generic import View
from .forms import InfoEmailForm
from .models import InfoEmail,Facture
import os.path

# Create your views here.

class InfoEmailView(CreateView):
    model = InfoEmail
    form_class = InfoEmailForm
    template_name = 'bdd/Creation_Email.html'
    success_url = 'success'

	
def successView(request):
    return HttpResponse('Success! Thank you for your message.')

def home(request):
    return render(request, 'bdd/home.html')

@login_required
def facture_pdf(request,id=None):
    facture = Facture.objects.get(id=id)
    nom_fichier = "%s.pdf"%facture.Numero_Facture
    fichier = facture.Fonction_Nom_Fichier_Facture()
	
    if not(os.path.exists(fichier)):
         return render(request,"bdd/facture/facture_no_fichier.html",{ "facture":facture })
		
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=%s'%nom_fichier
    with open(fichier,"rb") as f:
        response.write(f.read())
    return response

'''
def InfoEmailView(request,pk):

    return render(request, 'Visualisation_Facture2.html', context = data)
'''
