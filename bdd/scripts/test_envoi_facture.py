import django
django.setup()

from django.conf import settings
import bdd.models as BDD
from bdd.fonctions import *
from django.core.mail import EmailMessage
from django.core.files import File
from pathlib import Path
import tempfile

print("test envoi facture")
facture = BDD.Facture.objects.latest("id")
print(facture)
DOSSIER = settings.MEDIA_ROOT
#DOSSIER_TEMP = tempfile.TemporaryDirectory().name
DOSSIER_TEMP = DOSSIER + tempfile.TemporaryDirectory().name
DOSSIER_PRIVE = settings.MEDIA_ROOT_PRIVE

From = settings.DEFAULT_FROM_EMAIL
message = "Facture de test"
sujet = "test envoi facture"
RAR = None
Suivi = None
idfacture = None
typeaction = ""

affaire = BDD.Affaire.objects.get(pk=facture.ID_Affaire_id)
offre = BDD.Offre_Mission.objects.get(pk=affaire.ID_Mission_id)
ingeprev = BDD.Ingeprev.objects.get(Nom='INGEPREV')

#Création du pdf dans media
data = {}
data['facture'] = facture
data['Ref_Affaire'] = affaire.Ref_Affaire
data['affaire'] = affaire
data['Date_Echeance'] = facture.Date_Echeance1()
data['Montant_TTC'] = facture.Montant_Facture_TTC()
data['ingeprev'] = ingeprev
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

source_html = 'bdd/Visualisation_Facture2.html'
fichier = DOSSIER_TEMP + 'factures{}.pdf'.format(facture.Numero_Facture)
creer_html_to_pdf(source_html,fichier, data)
print('Fichier créé {}'.format(fichier))

obj = BDD.InfoEmail.objects.create(From = From, To=facture.Email_Facture, Message=message,
                                 Subject=sujet, RAR = RAR, Suivi = Suivi,
                                 ID_Facture=idfacture, Type_Action=typeaction)

chemin = Path(DOSSIER_PRIVE + 'factures/{}.pdf'.format(facture.Numero_Facture))
with chemin.open(mode='rb') as f:
    BDD.Attachment.objects.create(file=File(f, name=chemin.name), message=obj, nom = 'Facture')

Subject = obj.Subject
From = obj.From
Message = obj.Message
To = "gaudy.claire@gmail.com"

if True:
    attachments = []  # start with an empty list
    attach_files = BDD.Attachment.objects.filter(message_id = obj.pk)
	
    #email = EmailMessage(Subject, Message, From, [To], ['compta@ingeprev.com'], attachments = attachments) #Copie à compta@ingeprev.com
    email = EmailMessage(Subject, Message, From, [To], attachments=attachments)
	
    for attach in attach_files:
        print("ATTACH")
        f = settings.MEDIA_ROOT + attach.file.name
        #f = settings.MEDIA_URL + attach.file.name
        if isinstance(f, str):
            email.attach_file(f)
        elif isinstance(f, (tuple, list)):
            n, fi, mime = f + (None,) * (3 - len(f))
            email.attach(n, fi, mime)

    #email.content_subtype = "html"
    email.send()


