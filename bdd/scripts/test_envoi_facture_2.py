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
#DOSSIER_TEMP = DOSSIER + tempfile.TemporaryDirectory().name
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

obj = BDD.InfoEmail.objects.create(From = From, To=facture.Email_Facture, Message=message,
                                 Subject=sujet, RAR = RAR, Suivi = Suivi,
                                 ID_Facture=idfacture, Type_Action=typeaction)

chemin = facture.Fonction_Nom_Fichier_Facture()

Subject = obj.Subject
From = obj.From
Message = obj.Message
To = "gaudy.claire@gmail.com"

if True:
    attachments = []  # start with an empty list
    attach_files = chemin
	
    #email = EmailMessage(Subject, Message, From, [To], ['compta@ingeprev.com'], attachments = attachments) #Copie à compta@ingeprev.com
    email = EmailMessage(Subject, Message, From, [To], attachments=attachments)

    print("ATTACH")
    f = chemin
    #f = settings.MEDIA_URL + attach.file.name
    if isinstance(f, str):
            email.attach_file(f)
    elif isinstance(f, (tuple, list)):
            n, fi, mime = f + (None,) * (3 - len(f))
            email.attach(n, fi, mime)

    #email.content_subtype = "html"
    email.send()


