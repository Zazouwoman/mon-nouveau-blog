from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .models import Compteur_Indice,Client  #On importe le modèle pour pouvoir récuperer les données qui sont dedans
from .forms import ClientForm, InfoEmailForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import date
from django.http import HttpResponse
from django.views.generic import View
from . import models
from .fonctions import html_to_pdf
from django.template.loader import render_to_string

from django.core.mail import EmailMessage

from .forms import InfoEmailForm
from .models import InfoEmail
from django.views.generic.edit import FormView, CreateView

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