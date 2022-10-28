
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from django.conf import settings
from django.contrib.staticfiles import finders
from django.shortcuts import redirect
from .models import *
import os

def list_display_previsionnel(aujourdhui):
    L = []
    Ldescription = []
    k = 0
    L.append("fonction{}".format(k))
    Ldescription.append('antérieures')
    for k in range(1,13):
        debut, fin = debut_fin_mois(aujourdhui, k)
        mois = debut.month
        annee = debut.year
        L.append("fonction{}".format(k))
        Ldescription.append(str(mois) + '-' + str(annee))
    k = 13
    L.append("fonction{}".format(k))
    Ldescription.append('postérieures')
    return L, Ldescription

def list_entete_previsionnel(aujourdhui):
    Ldescription = ["Nom Affaire"] + ["Montant_Affaire","Deja_Facture"]
    k = 0
    Ldescription.append('antérieures')
    for k in range(1,13):
        debut, fin = debut_fin_mois(aujourdhui, k)
        mois = debut.month
        annee = debut.year
        Ldescription.append(str(mois) + '-' + str(annee))
    k = 13
    Ldescription.append('postérieures')
    return Ldescription

'''
def list_display_previsionnel(aujourdhui):
    global fonction0, fonction1,fonction2,fonction3,fonction4,fonction5,fonction6,fonction7,fonction8,fonction9,fonction10,fonction11,fonction12
    L = []
    Lfonction = []
    Ldescription = []

    k = 0
    debut, fin = debut_fin_mois(aujourdhui, k)
    mois = debut.month
    annee = debut.year
    def fonction0(self, obj):
        debut, fin = debut_fin_mois(aujourdhui, 0)
        debut = date(2022,9,1)
        print(debut)
        return obj.Montant_Entre_Date(debut, fin)
    L.append("fonction{}".format(k))
    Lfonction.append(fonction0)
    Ldescription.append('dates antérieures')

    k = 1
    debut, fin = debut_fin_mois(aujourdhui, k)
    mois = debut.month
    annee = debut.year
    def fonction1(self, obj):
        debut, fin = debut_fin_mois(aujourdhui, 1)
        return obj.Montant_Entre_Date(debut, fin)
    L.append("fonction{}".format(k))
    Lfonction.append(fonction1)
    Ldescription.append(str(mois) + '-' + str(annee))

    k = 2
    debut, fin = debut_fin_mois(aujourdhui, k)
    mois = debut.month
    annee = debut.year
    def fonction2(self, obj):
        debut, fin = debut_fin_mois(aujourdhui, 2)
        return obj.Montant_Entre_Date(debut, fin)
    L.append("fonction{}".format(k))
    Lfonction.append(fonction2)
    Ldescription.append(str(mois) + '-' + str(annee))

    k = 3
    debut, fin = debut_fin_mois(aujourdhui, k)
    mois = debut.month
    annee = debut.year
    def fonction3(self, obj):
        debut, fin = debut_fin_mois(aujourdhui, 3)
        return obj.Montant_Entre_Date(debut, fin)
    L.append("fonction{}".format(k))
    Lfonction.append(fonction3)
    Ldescription.append(str(mois) + '-' + str(annee))

    k = 4
    debut, fin = debut_fin_mois(aujourdhui, k)
    mois = debut.month
    annee = debut.year
    def fonction4(self, obj):
        debut, fin = debut_fin_mois(aujourdhui, 4)
        return obj.Montant_Entre_Date(debut, fin)
    L.append("fonction{}".format(k))
    Lfonction.append(fonction4)
    Ldescription.append(str(mois) + '-' + str(annee))

    k = 5
    debut, fin = debut_fin_mois(aujourdhui, k)
    mois = debut.month
    annee = debut.year
    def fonction5(self, obj):
        debut, fin = debut_fin_mois(aujourdhui, 5)
        return obj.Montant_Entre_Date(debut, fin)
    L.append("fonction{}".format(k))
    Lfonction.append(fonction5)
    Ldescription.append(str(mois) + '-' + str(annee))

    k = 6
    debut, fin = debut_fin_mois(aujourdhui, k)
    mois = debut.month
    annee = debut.year
    def fonction6(self, obj):
        debut, fin = debut_fin_mois(aujourdhui, 6)
        return obj.Montant_Entre_Date(debut, fin)
    L.append("fonction{}".format(k))
    Lfonction.append(fonction6)
    Ldescription.append(str(mois) + '-' + str(annee))

    k = 7
    debut, fin = debut_fin_mois(aujourdhui, k)
    mois = debut.month
    annee = debut.year
    def fonction7(self, obj):
        debut, fin = debut_fin_mois(aujourdhui, 7)
        return obj.Montant_Entre_Date(debut, fin)
    L.append("fonction{}".format(k))
    Lfonction.append(fonction7)
    Ldescription.append(str(mois) + '-' + str(annee))

    k = 8
    debut, fin = debut_fin_mois(aujourdhui, k)
    mois = debut.month
    annee = debut.year
    def fonction8(self, obj):
        debut, fin = debut_fin_mois(aujourdhui, 8)
        return obj.Montant_Entre_Date(debut, fin)
    L.append("fonction{}".format(k))
    Lfonction.append(fonction8)
    Ldescription.append(str(mois) + '-' + str(annee))

    k = 9
    debut, fin = debut_fin_mois(aujourdhui, k)
    mois = debut.month
    annee = debut.year
    def fonction9(self, obj):
        debut, fin = debut_fin_mois(aujourdhui, 9)
        return obj.Montant_Entre_Date(debut, fin)
    L.append("fonction{}".format(k))
    Lfonction.append(fonction9)
    Ldescription.append(str(mois) + '-' + str(annee))

    k = 10
    debut, fin = debut_fin_mois(aujourdhui, k)
    mois = debut.month
    annee = debut.year
    def fonction10(self, obj):
        debut, fin = debut_fin_mois(aujourdhui, 10)
        return obj.Montant_Entre_Date(debut, fin)
    L.append("fonction{}".format(k))
    Lfonction.append(fonction10)
    Ldescription.append(str(mois) + '-' + str(annee))

    k = 11
    debut, fin = debut_fin_mois(aujourdhui, k)
    mois = debut.month
    annee = debut.year
    def fonction11(self, obj):
        debut, fin = debut_fin_mois(aujourdhui, 11)
        return obj.Montant_Entre_Date(debut, fin)
    L.append("fonction{}".format(k))
    Lfonction.append(fonction11)
    Ldescription.append(str(mois) + '-' + str(annee))

    k = 12
    debut, fin = debut_fin_mois(aujourdhui, 12)
    mois = debut.month
    annee = debut.year
    def fonction12(self, obj):
        debut, fin = debut_fin_mois(aujourdhui, 12)
        return obj.Montant_Entre_Date(debut, fin)
    L.append("fonction{}".format(k))
    Lfonction.append(fonction12)
    Ldescription.append(str(mois) + '-' + str(annee))

    return L, Lfonction, Ldescription
'''

def debut_fin_mois(aujourdhui,k):
    #k représente le nombre de mois à rajouter
    mois = aujourdhui.month
    annee = aujourdhui.year
    debutmois = date(annee + (mois+k-1) // 12 , (mois + k - 1) % 12 + 1, 1)
    finmois = date(annee + (mois+k)//12, (mois+k)%12 + 1, 1) - timedelta(days=1)
    return debutmois,finmois

def creer_pdf_facture(facture,affaire,offre,ingeprev,dossier):
    """Crée le fichier pdf de la facture dans le dossier PRIVE
    Donnée nécessaire : obj,dossier"""

    #Création du pdf dans DOSSIER_PRIVE
    data = {}
    data['facture'] = facture
    data['Ref_Affaire'] = affaire.Ref_Affaire
    data['affaire'] = affaire
    data['Date_Echeance'] = facture.Date_Echeance1()
    data['Montant_TTC'] = facture.Montant_Facture_TTC()
    data['ingeprev'] = ingeprev
    data['mission'] = offre
    if facture.Facture_Avoir == "FA":
        data['FA'] = True
    else:
        data['FA'] = False
    data['datefactureliee'] = facture.Date_Facture_Liee()
    if adresses_identiques(facture):
        data['identiques'] = True
    else:
        data['identiques'] = False
    if adresses_completes_identiques(facture):
        data['completes_identiques'] = True
    else:
        data['completes_identiques'] = False
    if facture.Complement_Adresse_Facture == '':
        data['complementfacture'] = False
    else:
        data['complementfacture'] = True
    if facture.Complement_Adresse_Client == '':
        data['complementclient'] = False
    else:
        data['complementclient'] = True

    source_html = 'bdd/Visualisation_Facture2.html'
    fichier = dossier + 'factures/{}.pdf'.format(facture.Numero_Facture)
    creer_html_to_pdf(source_html,fichier, data)

    facture.Nom_Fichier_Facture = fichier
    facture.Date_Creation_Fichier_Facture = timezone.now()
    facture.Fichier_Facture_cree = True
    facture.save()


def creer_pdf_relance(k,facture,affaire,offre,ingeprev,dossier):
    """Crée le fichier pdf de la lettre de relance n°k dans dossier"""

    data = {}
    data['facture'] = facture
    data['Ref_Affaire'] = affaire.Ref_Affaire
    data['affaire'] = affaire
    data['Date_Echeance'] = facture.Date_Echeance1()
    data['Montant_TTC'] = facture.Montant_Facture_TTC()
    data['ingeprev'] = ingeprev
    data['mission'] = offre
    data['date'] = date.today()
    data['nb'] = facture.Nb_Avoir()
    data['avoir'] = facture.Avoirs_Lies()
    data['montant_avoir_lie'] = facture.Montants_Avoirs_Lies_TTC()
    data['solde'] = facture.Solde_Pour_Avoir_Eventuel()
    if facture.Facture_Avoir == "FA":
        data['FA'] = True
    else:
        data['FA'] = False
    if adresses_identiques(facture):
        data['identiques'] = True
    else:
        data['identiques'] = False
    if adresses_completes_identiques(facture):
        data['completes_identiques'] = True
    else:
        data['completes_identiques'] = False

    if facture.Complement_Adresse_Facture == '':
        data['complementfacture'] = False
    else:
        data['complementfacture'] = True
    if facture.Complement_Adresse_Client == '':
        data['complementclient'] = False
    else:
        data['complementclient'] = True
    if offre.Complement_Adresse == '':
        data['complementmission'] = False
    else:
        data['complementmission'] = True

    source_html = 'bdd/Lettre_Relance{}.html'.format(k)
    fichier = dossier + 'relances/Relance{}-{}.pdf'.format(k,facture.Numero_Facture)
    creer_html_to_pdf(source_html, fichier, data)
    if k == 2:
        facture.Nom_Fichier_Relance2 = fichier
        facture.Date_Creation_Fichier_Relance2 = timezone.now()
        facture.Fichier_Relance2_cree = True
    elif k == 3:
        facture.Nom_Fichier_Relance3 = fichier
        facture.Date_Creation_Fichier_Relance3 = timezone.now()
        facture.Fichier_Relance3_cree = True
    elif k == 4:
        facture.Nom_Fichier_Relance4 = fichier
        facture.Date_Creation_Fichier_Relance4 = timezone.now()
        facture.Fichier_Relance4_cree = True
    facture.save()


def adresses_identiques(facture):
    L1 = [facture.Denomination_Client, facture.Adresse_Client, facture.Complement_Adresse_Client, facture.CP_Client, facture.Ville_Client]
    L2 = [facture.Denomination_Facture, facture.Adresse_Facture, facture.Complement_Adresse_Facture, facture.CP_Facture, facture.Ville_Facture]
    return L1 == L2

def adresses_completes_identiques(facture):
    L1 = [facture.Denomination_Client, facture.Adresse_Client, facture.Complement_Adresse_Client, facture.CP_Client, facture.Ville_Client, facture.Civilite_Client, facture.Nom_Client, facture.Email_Client]
    L2 = [facture.Denomination_Facture, facture.Adresse_Facture, facture.Complement_Adresse_Facture, facture.CP_Facture, facture.Ville_Facture, facture.Civilite_Facture, facture.Nom_Facture, facture.Email_Facture
          ]
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

def message_facture_renvoi(facture, offre):
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
    message = civ + '\n\nFaisant suite à votre demande, nous vous prions de trouver ci-joint une nouvelle copie de la {} n° {} pour la mission de conseil en sécurité incendie sur le site du {} {} {}. \n\nBien cordialement, \n\nPour INGEPREV \n{}'.format(type,facture.Numero_Facture, offre.Adresse, offre.CP, offre.Ville, pilote)
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