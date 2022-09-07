
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from django.conf import settings
from django.contrib.staticfiles import finders
from django.shortcuts import redirect
from .models import *
import os

def adresses_identiques(facture):
    L1 = [facture.Denomination_Client, facture.Adresse_Client, facture.CP_Client, facture.Ville_Client]
    L2 = [facture.Denomination_Facture, facture.Adresse_Facture, facture.CP_Facture, facture.Ville_Facture]
    return L1 == L2

def adresses_completes_identiques(facture):
    L1 = [facture.Denomination_Client, facture.Adresse_Client, facture.CP_Client, facture.Ville_Client, facture.Civilite_Client, facture.Nom_Client, facture.Email_Client]
    L2 = [facture.Denomination_Facture, facture.Adresse_Facture, facture.CP_Facture, facture.Ville_Facture, facture.Civilite_Facture, facture.Nom_Facture, facture.Email_Facture]
    return L1 == L2

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

def message_relance(facture):
    civ = facture.Civilite_Facture
    if civ == 'M.':
        civ = 'Monsieur {},'.format(facture.Nom_Facture)
    elif civ == 'Mme':
        civ = 'Madame {},'.format(facture.Nom_Facture)
    else:
        civ = 'Madame, monsieur,'

    pilote = '{} {}'.format(facture.Prenom_Pilote, facture.Nom_Pilote)
    nb = facture.Nb_Avoir()
    if nb == 0:
        message = civ + """\n\nPar la présente nous nous permettons de vous rappeler que notre facture n°{} en date du {} vient d'arriver à échéance.\nSi vous venez de procéder à son paiement, nous vous prions de bien vouloir ne pas tenir compte de ce courriel.\n\nBien cordialement, \n\nPour INGEPREV \n{}""".format(facture.Numero_Facture, facture.Date_Facture.strftime('%d/%m/%Y'), pilote)
    elif nb == 1:
        L = facture.Avoirs_Lies()
        avoir = L[0]
        message = civ + """\n\nPar la présente nous nous permettons de vous rappeler que notre facture n°{} en date du {} vient d'arriver à échéance.\nPour mémoire, cette facture avait fait l'objet d'un avoir partiel n°{}.\nSi vous venez de procéder à son paiement, nous vous prions de bien vouloir ne pas tenir compte de ce courriel.\n\nBien cordialement, \n\nPour INGEPREV \n{}""".format(
            facture.Numero_Facture, facture.Date_Facture.strftime('%d/%m/%Y'), avoir, pilote)
    else:
        avoirs = ''
        L = facture.Avoirs_Lies()
        for k in range(len(L)-2):
            x = L[k]
            avoirs += 'n°{} ,'.format(x)
        avoirs += 'n°{} et n°{} '.format(L[len(L)-2], L[len(L)-1])
        message = civ + """\n\nPar la présente nous nous permettons de vous rappeler que notre facture n°{} en date du {} vient d'arriver à échéance.\nPour mémoire, cette facture avait fait l'objet des avoirs partiels {}.\nSi vous venez de procéder à son paiement, nous vous prions de bien vouloir ne pas tenir compte de ce courriel.\n\nBien cordialement, \n\nPour INGEPREV \n{}""".format(
            facture.Numero_Facture, facture.Date_Facture.strftime('%d/%m/%Y'), avoirs, pilote)
    return message

def message_facture(facture, offre):
    civ = facture.Civilite_Facture
    if civ == 'M.':
        civ = 'Monsieur {},'.format(facture.Nom_Facture)
    elif civ == 'Mme':
        civ = 'Madame {},'.format(facture.Nom_Facture)
    else:
        civ = 'Madame, monsieur,'

    if facture.Facture_Avoir =='FA':
        type = 'facture'
    else:
        type = 'avoir'

    pilote = '{} {}'.format(facture.Prenom_Pilote, facture.Nom_Pilote)
    message = civ + '\n\nNous vous prions de trouver ci-joint votre {} n° {} pour la mission de conseil en sécurité incendie sur le site du {} {} {}. \n\nBien cordialement, \n\nPour INGEPREV \n{}'.format(type,facture.Numero_Facture, offre.Adresse, offre.CP, offre.Ville, pilote)
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
    elif num == 6:
        facture.Date_Relance6 = date.today()
    facture.Date_Dernier_Rappel = date.today()
    facture.save()

def affichage_message_relance(messages, request, num):
    if num == 2:
        messages.add_message(request, messages.WARNING,
                             "Vous devez faire une relance par courrier suivi. Voici les documents à imprimer et à envoyer : facture + lettre. Vous avez aussi les coordonnées du contact si besoin. Remplissez le numéro de suivi pour pouvoir ensuite valider la relance.")
    elif num == 3:
        messages.add_message(request, messages.WARNING,
                                 "Vous devez faire une relance par courrier recommandé AR. Remplissez le numéro du RAR, validez pour obtenir la lettre de relance 3 à envoyer avec facture + lettre de relance 2. Vous pourrez ensuite valider la relance quand vous aurez imprimé et envoyé le courrier.")
    elif num == 4:
        messages.add_message(request, messages.WARNING,
                                 "Vous devez faire une mise en demeure. Commencez par rentrer le numéro du RAR pour obtenir la lettre de mise en demeure à envoyer avec facture + lettres de relance 2 + 3. Vous pourrez ensuite valider la relance quand vous aurez imprimé et envoyé le courrier.")
    elif num == 5:
        messages.add_message(request, messages.WARNING,
                                 """C'est l'heure de la conciliation. Vous trouverez ci-dessous les différents courriers envoyés ainsi que l'historique. Cliquez sur le bouton "Relance Faite" une fois la procédure de conciliation dûment engagée.""")
    elif num == 6:
        messages.add_message(request, messages.WARNING,
                                 """C'est l'heure de l'assignation. Vous trouverez ci-dessous les différents courriers envoyés ainsi que l'historique.  Cliquez sur le bouton "Relance Faite" une fois la procédure d'assignation dûment engagée.""")
    elif num >= 7:
        messages.add_message(request, messages.ERRORS,
                             "Nombre maximum de relances atteint.")
        return redirect('.')

def fetch_resources(uri, rel):
    path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path

def creer_html_to_pdf(sourcehtml, nompdf, data = {}):
    template = get_template(sourcehtml)
    html = template.render(data)
    fichier = nompdf
    write_to_file = open(fichier, "w+b")
    result = pisa.CreatePDF(html, dest=write_to_file, link_callback=fetch_resources)
    write_to_file.close()
    return HttpResponse(result.err)

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
    result = open(DOSSIER+'facture.pdf', 'w+b')
    print('ici')
    pisa.CreatePDF(html, dest=result, link_callback=fetch_resources)
    #pdf = pisa.CreatePDF(html, dest = result, link_callback=link_callback)
    #pisa_status = pisa.CreatePDF(html.content, dest=pdfFile, encoding='utf-8')
    if pdf.err:
        dumpErros(pdf)
    return pisa.startViewer(result)

def generate_pdf_through_template(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    #html = render_to_string(html)
    write_to_file = open(DOSSIER+'test_1.pdf', "w+b")
    pisa.CreatePDF(html, dest=write_to_file, link_callback=fetch_resources)
    #result = pisa.CreatePDF(html, dest=write_to_file, link_callback=link_callback)
    write_to_file.close()
    return HttpResponse(result.err)

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