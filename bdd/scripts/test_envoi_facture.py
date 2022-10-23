import django
django.setup()

from django.conf import settings
import bdd.models as BDD
from django.core.mail import EmailMessage
from django.core.files import File
from pathlib import Path
import tempfile

print("test envoi facture")
facture = BDD.Facture.objects.latest("id")
print(facture)
DOSSIER = settings.MEDIA_ROOT
DOSSIER_TEMP = tempfile.TemporaryDirectory().name

From = settings.DEFAULT_FROM_EMAIL
message = "Facture de test"
sujet = "test envoi facture"
RAR = None
Suivi = None
idfacture = None
typeaction = ""

obj = BDD.InfoEmail.objects.create(From = From, To=facture.Email_Facture, Message=message,
                                 Subject=sujet, RAR = RAR, Suivi = Suivi,
                                 ID_Facture=idfacture, Type_Action=typeaction)

chemin = Path(DOSSIER_TEMP + 'facture{}.pdf'.format(facture.Numero_Facture))
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


