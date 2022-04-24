
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from django.conf import settings
from django.contrib.staticfiles import finders
from django.shortcuts import redirect
from .models import *

def calcul_indice(type,periode):
    recherche = Compteur_Indice.objects.filter(Type_Dossier = type, Periode = periode)
    if not recherche.exists():
        indice = 1
        new = Compteur_Indice(Type_Dossier = type, Periode = periode, Compteur = indice)
        new.save()
    else:
        ligne = Compteur_Indice.objects.get(Type_Dossier = type, Periode = periode)
        indice = ligne.Compteur + 1
        ligne.Compteur += 1
        ligne.save(update_fields=['Compteur'])
    return indice

def message_relance(facture, affaire):
    civ = facture.Civilite_Facture
    if civ == 'M.':
        civ = 'Bonjour monsieur {},'.format(civ, facture.Nom_Facture)
    elif civ == 'Mme':
        civ = 'Bonjour madame {},'.format(civ, facture.Nom_Facture)
    else:
        civ = 'Bonjour,'
    nomaffaire = affaire.Nom_Affaire
    pilote = '{} {}'.format(facture.Prenom_Pilote, facture.Nom_Pilote)
    message = civ + '\n\n Veuillez trouver ci-joint votre facture n°{} pour la mission {}. \n\n Bien cordialement, \n\n {}'.format(
        facture.Numero_Facture, nomaffaire, pilote)
    return message

def message_facture(facture, affaire):
    civ = facture.Civilite_Facture
    if civ == 'M.':
        civ = 'Bonjour monsieur {},'.format(civ, facture.Nom_Facture)
    elif civ == 'Mme':
        civ = 'Bonjour madame {},'.format(civ, facture.Nom_Facture)
    else:
        civ = 'Bonjour,'
    nomaffaire = affaire.Nom_Affaire
    pilote = '{} {}'.format(facture.Prenom_Pilote, facture.Nom_Pilote)
    message = civ + '\n\n Veuillez trouver ci-joint votre facture n°{} pour la mission {}. \n\n Bien cordialement, \n\n {}'.format(
        facture.Numero_Facture, nomaffaire, pilote)
    return message

def mise_a_jour_relance(facture, num):  #mise à jour des dates de la facture lors de relance ou envoi facture
    facture.Num_Relance = num + 1
    if num == 0:
        facture.deja_envoyee = True
        facture.Etat = 'ENV'
        facture.Date_Envoi = date.today()
    if num == 1:
        facture.Date_Relance1 = date.today()
    elif num == 2:
        facture.Date_Relance2 = date.today()
    elif num == 3:
        facture.Date_Relance3 = date.today()
    elif num == 4:
        facture.Date_Relance4 = date.today()
    elif num == 5:
        facture.Date_Relance5 = date.today()
    facture.Date_Dernier_Rappel = date.today()
    facture.save()

def affichage_message_relance(messages, request, num):
    if num == 2:
        messages.add_message(request, messages.INFO,
                             "Vous devez faire une relance téléphonique. Voici les coordonnées du contact. Validez la relance quand c'est effectué.")
    elif num == 3:
        messages.add_message(request, messages.INFO,
                             "Vous devez faire une relance par courrier. Voici les courriers à imprimer et à envoyer : facture + lettre. Validez la relance quand c'est effectué ")
    elif num == 4:
        messages.add_message(request, messages.INFO,
                                 "Vous devez faire une relance par courrier recommandé AR. Remplir le numéro du RAR, valider pour obtenir la lettre. Validez ensuite la relance quand c'est effectué.")
    elif num == 5:
        messages.add_message(request, messages.INFO,
                                 "Vous devez faire une mise en demeure. Validez ensuite la relance quand c'est effectué.")
    elif num >= 6:
        messages.add_message(request, messages.INFO,
                             "Nombre maximum de relances atteint.")
        return redirect('.')

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path

def creer_html_to_pdf(sourcehtml, nompdf, data = {}):
    template = get_template(sourcehtml)
    html = template.render(data)
    fichier = nompdf
    write_to_file = open(fichier, "w+b")
    result = pisa.CreatePDF(html, dest=write_to_file, link_callback=link_callback)
    write_to_file.close()
    return HttpResponse(result.err)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='bdd/pdf')
    return None


def html_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    #pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result, errors='ignore')
    print('ici')
    #pisa_status = pisa.CreatePDF(html.content, dest=pdfFile, encoding='utf-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='bdd/pdf')
    return None

def html_to_pdf2(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = open('media/facture.pdf', 'w+b')
    print('ici')
    pdf = pisa.CreatePDF(html, dest = result, link_callback=link_callback)
    #pisa_status = pisa.CreatePDF(html.content, dest=pdfFile, encoding='utf-8')
    if pdf.err:
        dumpErros(pdf)
    return pisa.startViewer(result)


def generate_pdf_through_template(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    #html = render_to_string(html)
    write_to_file = open('media/test_1.pdf', "w+b")
    result = pisa.CreatePDF(html, dest=write_to_file, link_callback=link_callback)
    write_to_file.close()
    return HttpResponse(result.err)