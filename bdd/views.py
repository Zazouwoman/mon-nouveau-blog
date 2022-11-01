from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView, CreateView
from django.http import HttpResponse
from django.views.generic import View
from .forms import InfoEmailForm
from .models import InfoEmail,Facture,Attachment,Fichier_Word
import os.path
import io
from docx import Document

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
def lien_fichier_word2(request, id=None):
    fichierword = Fichier_Word.objects.get(id=id)
    print('ici',fichierword)
    nom_fichier = fichierword.Word2  # C'est le nom que l'on veut que le fichier ait
    print('ici2',nom_fichier)
    fichier = fichierword.Word2.path
    print('ici3',fichier)

    if not (os.path.exists(fichier)):
        return render(request, "bdd/no_fichier.html", {"facture": fichierword})

    response = HttpResponse(content_type='application/vnd.ms-word')
    response = HttpResponse(content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'inline; filename=%s' % nom_fichier
    with open(fichier, "rb") as f:
        response.write(f.read())
    return response

@login_required
def lien_fichier_word3(request, id=None):
    fichierword = Fichier_Word.objects.get(id=id)
    print('ici',fichierword)
    nom_fichier = fichierword.Word3  # C'est le nom que l'on veut que le fichier ait
    print('ici2',nom_fichier)
    fichier = fichierword.Fonction_Nom_Fichier_Word3()

    if not (os.path.exists(fichier)):
        return render(request, "bdd/no_fichier.html", {"facture": fichierword})

    response = HttpResponse(content_type='application/vnd.ms-word')
    #response = HttpResponse(content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'inline; filename=%s' % nom_fichier
    with open(fichier, "rb") as f:
        response.write(f.read())
    return response
@login_required
def lien_fichier_word4(request, id=None):
    fichierword = Fichier_Word.objects.get(id=id)
    print('ici',fichierword)
    nom_fichier = fichierword.Word4  # C'est le nom que l'on veut que le fichier ait
    print('ici2',nom_fichier)
    fichier = fichierword.Fonction_Nom_Fichier_Word4()

    if not (os.path.exists(fichier)):
        return render(request, "bdd/no_fichier.html", {"facture": fichierword})

    response = HttpResponse(content_type='application/vnd.ms-word')
    #response = HttpResponse(content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'inline; filename=%s' % nom_fichier
    with open(fichier, "rb") as f:
        response.write(f.read())
    return response

@login_required
def relance_word2(request, id=None):
    facture = Facture.objects.get(id=id)
    document = facture.relance2_word()

    # save document info
    buffer = io.BytesIO()
    document.save(buffer)  # save your memory stream
    buffer.seek(0)  # rewind the stream

    response = HttpResponse(content=buffer,content_type='application/vnd.ms-word')
    response['Content-Disposition'] = 'inline; filename=Relance2-{}.docx'.format(facture.Numero_Facture)
    response["Content-Encoding"] = 'UTF-8'
    return response
@login_required
def relance_word3(request, id=None):
    facture = Facture.objects.get(id=id)
    document = facture.relance3_word()
    # save document info
    buffer = io.BytesIO()
    document.save(buffer)  # save your memory stream
    buffer.seek(0)  # rewind the stream

    response = HttpResponse(content=buffer,content_type='application/vnd.ms-word')
    response['Content-Disposition'] = 'inline; filename=Relance3-{}.docx'.format(facture.Numero_Facture)
    response["Content-Encoding"] = 'UTF-8'
    return response
@login_required
def relance_word4(request, id=None):
    facture = Facture.objects.get(id=id)
    document = facture.relance4_word()

    # save document info
    buffer = io.BytesIO()
    document.save(buffer)  # save your memory stream
    buffer.seek(0)  # rewind the stream

    response = HttpResponse(content=buffer,content_type='application/vnd.ms-word')
    response['Content-Disposition'] = 'inline; filename=Relance4-{}.docx'.format(facture.Numero_Facture)
    response["Content-Encoding"] = 'UTF-8'
    return response

@login_required
def relance_word2bis(request, id=None):
    facture = Facture.objects.get(id=id)
    nom_fichier = "Relance2-{}.docx".format(facture.Numero_Facture)  # C'est le nom que l'on veut que le fichier ait
    fichier = facture.Fonction_Nom_Fichier_Word_Relance(2)

    if not (os.path.exists(fichier)):
        return render(request, "bdd/facture/facture_no_fichier.html", {"facture": facture})

    response = HttpResponse(content_type='application/vnd.ms-word')
    response['Content-Disposition'] = 'inline; filename=%s' % nom_fichier
    with open(fichier, "rb") as f:
        response.write(f.read())
    return response
@login_required
def relance_word3bis(request, id=None):
    facture = Facture.objects.get(id=id)
    nom_fichier = "Relance3-{}.docx".format(facture.Numero_Facture)  # C'est le nom que l'on veut que le fichier ait
    fichier = facture.Fonction_Nom_Fichier_Word_Relance(3)

    if not (os.path.exists(fichier)):
        return render(request, "bdd/facture/facture_no_fichier.html", {"facture": facture})

    response = HttpResponse(content_type='application/vnd.ms-word')
    response['Content-Disposition'] = 'inline; filename=%s' % nom_fichier
    with open(fichier, "rb") as f:
        response.write(f.read())
    return response
@login_required
def relance_word4bis(request, id=None):
    facture = Facture.objects.get(id=id)
    nom_fichier = "Relance4-{}.docx".format(facture.Numero_Facture)  # C'est le nom que l'on veut que le fichier ait
    fichier = facture.Fonction_Nom_Fichier_Word_Relance(4)

    if not (os.path.exists(fichier)):
        return render(request, "bdd/facture/facture_no_fichier.html", {"facture": facture})

    response = HttpResponse(content_type='application/vnd.ms-word')
    response['Content-Disposition'] = 'inline; filename=%s' % nom_fichier
    with open(fichier, "rb") as f:
        response.write(f.read())
    return response

@login_required
def relance_pdf2(request, id=None):
    facture = Facture.objects.get(id=id)
    nom_fichier = "Relance2-{}.pdf".format(facture.Numero_Facture)  # C'est le nom que l'on veut que le fichier ait
    fichier = facture.Fonction_Nom_Fichier_Pdf_Relance(2)

    if not (os.path.exists(fichier)):
        return render(request, "bdd/facture/facture_no_fichier.html", {"facture": facture})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=%s' % nom_fichier
    with open(fichier, "rb") as f:
        response.write(f.read())
    return response
@login_required
def relance_pdf3(request, id=None):
    facture = Facture.objects.get(id=id)
    nom_fichier = "Relance3-{}.pdf".format(facture.Numero_Facture)  # C'est le nom que l'on veut que le fichier ait
    fichier = facture.Fonction_Nom_Fichier_Pdf_Relance(3)

    if not (os.path.exists(fichier)):
        return render(request, "bdd/facture/facture_no_fichier.html", {"facture": facture})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=%s' % nom_fichier
    with open(fichier, "rb") as f:
        response.write(f.read())
    return response
@login_required
def relance_pdf4(request, id=None):
    facture = Facture.objects.get(id=id)
    nom_fichier = "Relance4-{}.pdf".format(facture.Numero_Facture)  # C'est le nom que l'on veut que le fichier ait
    fichier = facture.Fonction_Nom_Fichier_Pdf_Relance(4)

    if not (os.path.exists(fichier)):
        return render(request, "bdd/facture/facture_no_fichier.html", {"facture": facture})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=%s' % nom_fichier
    with open(fichier, "rb") as f:
        response.write(f.read())
    return response

@login_required
def facture_pdf(request,id=None):
    facture = Facture.objects.get(id=id)
    nom_fichier = "%s.pdf"%facture.Numero_Facture  #C'est le nom que l'on veut que le fichier ait
    fichier = facture.Fonction_Nom_Fichier_Facture()
	
    if not(os.path.exists(fichier)):
         return render(request,"bdd/facture/facture_no_fichier.html",{ "facture":facture })
		
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=%s'%nom_fichier
    with open(fichier,"rb") as f:
        response.write(f.read())
    return response

@login_required
def attachment_pdf(request, id=None):
    attachment = Attachment.objects.get(id=id)
    nom_fichier = attachment.Nom_Fichier_Joint()
    fichier = attachment.Chemin_Fichier()

    if not (os.path.exists(fichier)):
        return render(request, "bdd/no_fichier.html", {"facture": fichier})

    print('on est là')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=%s' % nom_fichier
    with open(fichier, "rb") as f:
        response.write(f.read())
    return response

'''
def InfoEmailView(request,pk):

    return render(request, 'Visualisation_Facture2.html', context = data)
'''
