from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView, CreateView
from django.http import HttpResponse
from django.views.generic import View

from .forms import InfoEmailForm
from .models import InfoEmail

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
