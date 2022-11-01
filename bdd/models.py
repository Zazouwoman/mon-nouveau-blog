
from django.db import models
from django.db.models import Sum,Max
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib import admin

# Create your models here.

from django.core.validators import RegexValidator
from django.core.mail.backends.smtp import EmailBackend

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from django.forms.utils import flatatt

from django.utils.safestring import mark_safe
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib import messages

from decimal import Decimal
from .fonctions import *
from .fonctionsWord import *
from django.core.exceptions import ValidationError
from pathlib import Path
import tempfile

from docx import Document
from docx.shared import Inches
from docx.shared import Pt,Cm
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH,WD_LINE_SPACING

import shutil
#from docx2pdf import convert
#import pythoncom
import os.path

DOSSIER = settings.MEDIA_ROOT #Nom du dossier public dans lequel sont enregistrés les factures, lettres de relance
DOSSIER_PRIVE = settings.MEDIA_ROOT_PRIVE #Nom du dossier privé dans lequel sont enregistrés les factures, lettres de relance ...
#DOSSIER_TEMP = tempfile.TemporaryDirectory(prefix="facture-").name
#DOSSIER_TEMP = tempfile.TemporaryDirectory().name
DOSSIER_TEMP = DOSSIER + tempfile.TemporaryDirectory().name

def mois_annee(date):
    return date.mois,date.year

def formater_tel(tel_int):
    tel_str = str(tel_int)
    numeros = [tel_str[x:x+2] for x in range(0,len(tel_str),2)]
    return '.'.join(numeros)

def formater_IBAN(iban):
    iban_str = str(iban)
    numeros = [iban_str[x:x+4] for x in range(0,len(iban_str),4)]
    return ' '.join(numeros)

def formater_SIRET(SIRET):
    siret_str = str(SIRET)
    numeros = [siret_str[:3] , siret_str[3:6], siret_str[6:9], siret_str[9:]]
    return ' '.join(numeros)

def date_derniere_facture():
    datemax=Facture.objects.all().aggregate(Max('Date_Facture'))['Date_Facture__max']
    return datemax

def calcul_indice(type,periode):
    recherche = Compteur_Indice.objects.filter(Type_Dossier = type, Periode = periode)
    if not recherche.exists():
        indice = 1
        new = Compteur_Indice(Type_Dossier = type, Periode = periode, Compteur = indice)
        new.save()
    else:
        ligne = Compteur_Indice.objects.get(Type_Dossier=type, Periode=periode)
        indice = ligne.Compteur + 1
        ligne.Compteur += 1
        ligne.save(update_fields=['Compteur'])
    return indice

def creer_Envoi_Facture(ID_Client):
    """Etant donné l'id d'un client existant, crée une adresse d'envoi de facture
    avec les mêmes valeurs. Les conditions de paiement étant aux valeurs par défaut."""
    client = Client.objects.get(pk=ID_Client)
    denomination = client.Denomination_Sociale
    adresse = client.Adresse
    complement_adresse = client.Complement_Adresse
    cp = client.CP
    ville = client.Ville
    civ = client.Civilite
    nom = client.Nom_Representant
    prenom = client.Prenom_Representant
    tel = client.Tel_Representant
    email = client.Email_Representant
    qs = Envoi_Facture.objects.filter(Denomination_Sociale=denomination, Adresse=adresse,
                                      Complement_Adresse=complement_adresse,CP=cp, Ville=ville, Civilite=civ,
                                  Nom_Contact=nom, Prenom_Contact=prenom, Tel_Contact=tel, Email_Contact=email,
                                   Mode_Paiement = "VI", Delais_Paiement = 30, Fin_Mois = "Non", Modalites_Paiement = ""   )
    if qs.count() >= 1:
        envoi_facture = qs[0]
    else:
        envoi_facture = Envoi_Facture.objects.create(Denomination_Sociale=denomination, Adresse=adresse,
                                                     Complement_Adresse=complement_adresse,
                                                     CP=cp, Ville=ville, Civilite=civ,
                                  Nom_Contact=nom, Prenom_Contact=prenom, Tel_Contact=tel, Email_Contact=email, )
    return envoi_facture

CiviliteType = models.TextChoices('civ', 'M. Mme')
tel_regex = RegexValidator(regex=r"^\+?1?\d{8,15}$", message=(
    "Un numero de téléphone est attendu."))
CP_regex = RegexValidator(regex=r'^[0-9]+$', message=(
    "le code postal doit être composé de 5 chiffres."))
ModePaiementType = [ ('ND', "Non défini"), ("VI", "Virement"), ("CH", "Chèque"), ("CB", "Carte Bancaire"),
                     ("ES","Espèces")]
OuiOuNonType = models.TextChoices("OuiOuNonType","Oui Non")
EtatType = [("ATT","En Attente"), ("ACC","Acceptée"),("REF","Sans suite")]
AffaireType = [("C","Conseil"),("AMO","AMO"),("DA","Diag/Audit")]
EtatAffaireType = [("EC", "En Cours"), ("ARC", "Archivée")]
FactureType = [('FA','Facture'),('AV','Avoir')]
EtatFacture = [("BR","Brouillon"),("VA","Validée"),('ENV',"Envoyée")]
EtatPaiement = [("ATT","En Attente"),("PAYE","Payée")]
TVA = [('20','20'),('10','10'),('5','5'),('0','0')]
DelaisPaiement=[('30','30'),('60','60')]

class Ingeprev(models.Model):
    Nom = models.CharField(max_length=50, blank=True, verbose_name = 'Nom de la societe')
    logo = models.ImageField(upload_to='images/',null=True,blank=True)
    SIRET = models.CharField(max_length=50, blank=True, verbose_name="N° de SIRET (saisir sans espace)")
    Adresse = models.CharField(max_length=500, blank=True)
    Complement_Adresse = models.CharField(max_length=500, blank=True, verbose_name = "Complément d'Adresse")
    CP = models.CharField(validators=[CP_regex], max_length=5, verbose_name='Code postal', blank=True)
    Ville = models.CharField(max_length=150, blank=True)
    Type_Societe = models.CharField(max_length=150, blank=True, verbose_name = 'Statut juridique')
    Code_Banque = models.CharField(max_length= 6,blank=True, null = True, verbose_name = 'Code Banque (saisir sans espaces)')
    Code_Guichet = models.CharField(max_length = 6, blank=True, null = True, verbose_name='Code Guichet (saisir sans espaces)')
    Code_BIC = models.CharField(max_length=20, blank=True, verbose_name='Code BIC')
    Num_Compte = models.CharField(max_length=20,null=True, blank = True, verbose_name='Numéro de Compte (saisir sans espaces)')
    Cle = models.CharField(max_length=10, blank=True, verbose_name = 'Clé')
    Nom_Banque = models.CharField(max_length=100, blank=True, verbose_name = 'Nom de la Banque')
    Tel_Banque = models.CharField(validators=[tel_regex], max_length=16, verbose_name='Numéro de Téléphone de la banque',
                                        blank=True)
    IBAN = models.CharField(max_length=50, blank=True, verbose_name = 'IBAN (saisir sans espaces)')
    Code_APE = models.CharField(max_length=150, blank=True, verbose_name='Code APE')
    Capital = models.DecimalField(max_digits=15, decimal_places=2, verbose_name = 'Capital', default =0, blank = True)
    Num_TVA = models.CharField(max_length=150, blank=True, verbose_name = 'N° de TVA Intercommunautaire')
    Email = models.EmailField(max_length=70, blank=True)
    Tel = models.CharField(validators=[tel_regex], max_length=16, verbose_name='Numéro de Téléphone',
                                        blank=True)
    Site_Web = models.URLField(max_length=300, blank = True)
    Facebook = models.URLField(max_length=300, blank=True)
    Twitter = models.URLField(max_length=300, blank=True)
    Linkedin = models.URLField(max_length=300, blank = True)

    class Meta:
        verbose_name_plural = "6. INGEPREV"

    def delete(self,*args,**kwargs):
        obj = Ingeprev.objects.get(pk = self.pk)
        obj.logo.delete()
        if os.path.isfile(self.logo.path):
            os.remove(self.logo.path)
        super(Ingeprev, self).delete(*args,**kwargs)

    def Tel_Banque_Affiche(self):
        return formater_tel(self.Tel_Banque)

    def Tel_Affiche(self):
        return formater_tel(self.Tel)

    def IBAN_Affiche(self):
        return formater_IBAN(self.IBAN)

    def SIRET_Affiche(self):
        return formater_SIRET(self.SIRET)

class Pilote(models.Model):
    Civilite = models.CharField(blank=True, choices=CiviliteType.choices, max_length=3)
    Nom = models.CharField(max_length=50, blank=True)
    Prenom = models.CharField(max_length=50, blank=True)
    Tel_Portable = models.CharField(validators=[tel_regex], max_length=16, verbose_name='Numéro de Portable',
                                        blank=True)
    Tel_Fixe = models.CharField(validators=[tel_regex], max_length=16, verbose_name='numéro de Fixe',
                                    blank=True)
    Email = models.EmailField(max_length=70, blank=True)

    def __str__(self):
        return "{} {}".format(self.Nom, self.Prenom)

    class Meta:
        ordering = ['Nom']
        verbose_name_plural = "5. Pilotes"

class Client(models.Model):
    Type_Dossier = models.CharField(default = "C",max_length = 3)
    Indice_Dossier = models.IntegerField(default = 0,blank=True)
    Numero_Client = models.CharField(default = "C0001",max_length = 50, verbose_name = "Numéro de Client")
    Denomination_Sociale = models.CharField(max_length = 150, verbose_name = "Dénomination sociale")
    SIRET = models.CharField(max_length = 50,blank=True, verbose_name = "N° de SIRET")
    Adresse = models.CharField(max_length = 500,blank=True)
    Complement_Adresse = models.CharField(max_length=500, blank=True)
    CP = models.CharField(validators=[CP_regex], max_length=5, verbose_name='Code postal',blank=True)
    Ville = models.CharField(max_length = 150,blank=True)
    Civilite = models.CharField(blank = True,choices = CiviliteType.choices,max_length = 3)
    Nom_Representant = models.CharField(max_length = 50,blank=True, verbose_name = "Nom")
    Prenom_Representant = models.CharField(max_length = 50,blank=True, verbose_name = "Prénom")
    Tel_Representant = models.CharField(validators=[tel_regex], max_length=16, verbose_name='Numéro de téléphone',blank=True)
    Email_Representant = models.EmailField(max_length=70,blank=True, verbose_name = "Email")

    def Total_Affaire(self):
        ID = self.id
        total = 0
        for element in Affaire.objects.all():
            print(element.ID_Client_Cache)
            if element.ID_Client_Cache == None:
                if element.ID_Payeur_id == ID:
                    total += element.Honoraires_Global
        resultat1 = Affaire.objects.filter(ID_Client_Cache = ID).aggregate(Honoraires_Global=Sum('Honoraires_Global'))['Honoraires_Global'] or 0
        return total + resultat1

    Total_Affaire.short_description = "Montant total des affaires du client"

    def save(self,*args,**kwargs):
        if self.Numero_Client == 'C0001':
            aujourdhui = date.today()
            annee = aujourdhui.year
            mois = aujourdhui.month
            periode = '{}{:02d}'.format(annee,mois)
            indice = calcul_indice('C', periode)
            self.Numero_Client = 'C-{}{:04d}'.format(periode,indice)
            self.Indice_Dossier = indice
        super().save(*args,**kwargs)

    def get_absolute_url(self):
        return reverse('librairie : Client', kwargs={'pk': self.pk})

    def __str__(self):
        return "{} , {} ".format(self.Denomination_Sociale, self.SIRET)

    class Meta:
        ordering = ['Denomination_Sociale']
        verbose_name_plural = "4. Clients"

class Compteur_Indice(models.Model):
    Type_Dossier = models.CharField(max_length = 3)
    Periode = models.CharField(max_length = 10)  #yyyymm
    Compteur = models.IntegerField()

class Envoi_Offre(models.Model):
    Denomination_Sociale = models.CharField(max_length=50, verbose_name = "Dénomination Sociale")
    Adresse = models.CharField(max_length=500, blank=True)
    Complement_Adresse = models.CharField(max_length=500, blank=True)
    CP = models.CharField(validators=[CP_regex], max_length=5, verbose_name='Code postal', blank=True)
    Ville = models.CharField(max_length=150, blank=True)
    Civilite = models.CharField(blank=True, choices=CiviliteType.choices, max_length=3)
    Nom_Contact = models.CharField(max_length=50, blank=True, verbose_name = "Nom")
    Prenom_Contact = models.CharField(max_length=50, blank=True, verbose_name = "Prénom")
    Tel_Contact = models.CharField(validators=[tel_regex], max_length=16, verbose_name='Numéro de téléphone',
                                        blank=True)
    Email_Contact = models.EmailField(max_length=70, blank=True, verbose_name = "Email")

    def get_absolute_url(self):
        return reverse('librairie : Envoi_Offre', kwargs={'pk': self.pk})

    def __str__(self):
        return "{} , {} ".format(self.Denomination_Sociale, self.Nom_Contact)

    class Meta:
        ordering = ['Denomination_Sociale', 'Nom_Contact']

class Envoi_Facture(models.Model):
    Denomination_Sociale = models.CharField(max_length=150, verbose_name = "Dénomination sociale")
    Adresse = models.CharField(max_length=500, blank = True)
    Complement_Adresse = models.CharField(max_length=500, blank=True)
    CP = models.CharField(validators=[CP_regex], max_length=5, verbose_name='Code postal', blank = True)
    Ville = models.CharField(max_length=150, blank = True)
    Civilite = models.CharField(blank=True, choices=CiviliteType.choices, max_length=3)
    Nom_Contact = models.CharField(max_length=50, blank=True, verbose_name = "Nom")
    Prenom_Contact = models.CharField(max_length=50, blank=True, verbose_name = "Prénom")
    Tel_Contact = models.CharField(validators=[tel_regex], max_length=16, verbose_name='Numéro de téléphone',
                                        blank=True)
    Email_Contact = models.EmailField(max_length=70, blank=True, verbose_name = 'Email')
    Mode_Paiement = models.CharField(default = "VI", choices = ModePaiementType, max_length = 20, verbose_name = "Mode de Paiement")
    Delais_Paiement = models.CharField(choices = DelaisPaiement, max_length=3,default = '30', verbose_name = "Délais de Paiement (en jours)")
    Fin_Mois = models.CharField(choices = OuiOuNonType.choices , max_length = 3, default = "Oui", verbose_name = "Fin de Mois")
    Modalites_Paiement = models.TextField(blank = True, verbose_name = "Modalités particulières de Paiement")

    def get_absolute_url(self):
        return reverse('admin : bdd_Envoi_Facture_change', kwargs={'pk': self.pk})

    def __str__(self):
        return "{} , {} ".format(self.Denomination_Sociale, self.Nom_Contact)

    class Meta:
        ordering = ['Denomination_Sociale', 'Nom_Contact']


class Offre_Mission(models.Model):
    Type_Dossier = models.CharField(default = "OM",max_length = 3)
    Indice_Dossier = models.IntegerField(default = 0,blank=True)
    Ref_Mission = models.CharField(default = "OM0001",max_length = 50, verbose_name = "Réf. Mission")
    Nom_Mission = models.CharField(max_length = 100, verbose_name = "Nom de la mission")
    Adresse = models.CharField(max_length=500, blank=True)
    Complement_Adresse = models.CharField(max_length=500, blank=True)
    CP = models.CharField(validators=[CP_regex], max_length=5, verbose_name='Code postal', blank=True)
    Ville = models.CharField(max_length=150, blank=True)
    ID_Payeur = models.ForeignKey(Client,on_delete=models.SET_NULL, related_name='%(class)s_ID_Payeur', blank = True, verbose_name = "Payeur", null = True)
    ID_Envoi_Offre = models.ForeignKey(Envoi_Offre,on_delete=models.SET_NULL, blank = True, verbose_name = "Adresse Envoi Offre", null = True)
    ID_Client_Cache = models.ForeignKey(Client, on_delete=models.SET_NULL,  related_name='%(class)s_ID_Client_Cache', blank = True, verbose_name = "Client Caché", null = True)
    ID_Apporteur = models.ForeignKey(Client, on_delete=models.SET_NULL, blank = True,  related_name='%(class)s_ID_Apporteur', verbose_name = "Apporteur d'affaire", null = True)
    Honoraires_Proposes = models.DecimalField(max_digits=12, decimal_places=2, verbose_name = 'Honoraires H.T.', default = 0)
    Date_Proposition = models.DateField(default=date.today, verbose_name = "Date de Proposition")
    Date_Acceptation = models.DateField(blank = True, null = True, default = None, verbose_name = "Date d'acceptation")
    Descriptif = models.TextField()
    Etat = models.CharField(choices = EtatType, max_length = 20, default = "ATT")
    ID_Pilote = models.ForeignKey(Pilote, on_delete=models.SET_NULL, verbose_name = "Pilote", blank = True, null = True)

    def custom_delete(self):
        if self.Etat != 'ACC':
            self.delete()

    def Client(self):
        client = None
        IDCC = self.ID_Client_Cache_id
        if IDCC != None:
            client_cache = Client.objects.get(id=IDCC)
            client = client_cache.Denomination_Sociale
        else:
            ID = self.ID_Envoi_Offre_id
            if ID != None:
                envoi_offre = Envoi_Offre.objects.get(id=ID)
                client = envoi_offre.Denomination_Sociale
            else:
                idpayeur = self.ID_Payeur_id
                payeur = Client.objects.get(id=idpayeur)
                client = payeur.Denomination_Sociale
        return client

    def get_absolute_url(self):
        return reverse('admin : bdd_Offre_Mission_change', kwargs={'pk': self.pk})

    def __str__(self):
        return "{} , {} ".format(self.Nom_Mission,self.Ref_Mission)

    class Meta:
        ordering = ['Nom_Mission']
        verbose_name_plural = "1. Offres de Mission"

    def save(self,*args,**kwargs):
        if self.Ref_Mission == 'OM0001':
            aujourdhui = date.today()
            annee = aujourdhui.year
            mois = aujourdhui.month
            periode = '{}{:02d}'.format(annee,mois)
            indice = calcul_indice('OM', periode)
            self.Ref_Mission = 'OM-{}{:04d}'.format(periode,indice)
            self.Indice_Dossier = indice
        super().save(*args,**kwargs)

class Affaire(models.Model):
    soldee = models.BooleanField(default = 'False', verbose_name = "Archivée")  #Pour savoir si l'affaire est soldée
    previsionnelcree = models.BooleanField(default='False', verbose_name="Prévisionnel Créé")  # Pour savoir si le prévisionnel a été créé
    Type_Dossier = models.CharField(default = "A",max_length = 3)
    Indice_Dossier = models.IntegerField(default = 0,blank=True)
    Ref_Affaire = models.CharField(default = "A0001",max_length = 50, verbose_name = "Réf. Affaire")
    Nom_Affaire = models.CharField(max_length = 100, verbose_name = "Nom de l'Affaire", blank = True, null = True)
    ID_Mission = models.OneToOneField(Offre_Mission , on_delete=models.CASCADE, verbose_name = "Nom de la mission")
    ID_Client_Cache = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='%(class)s_ID_Client_Cache', blank=True,verbose_name="Client Caché", null=True)
    ID_Payeur = models.ForeignKey(Client,on_delete=models.SET_NULL, related_name='%(class)s_ID_Payeur', blank = True, verbose_name = "Payeur", null = True)
    ID_Envoi_Facture = models.ForeignKey(Envoi_Facture,on_delete=models.SET_NULL, blank = True, verbose_name = "Adresse Envoi Facture", null = True)
    Ref_Client = models.CharField(max_length=150,blank = True, verbose_name="Référence Client à rappeler")
    Honoraires_Global = models.DecimalField(max_digits=12, decimal_places=2, verbose_name = 'Honoraire Global H.T.', default = 0)
    Date_Creation = models.DateField(default=date.today, verbose_name = "Date de création")
    Date_Previsionnelle = models.DateField(blank = True, null = True, default = None, verbose_name = "Date prévisionnelle de facturation")
    Type_Affaire = models.CharField(choices = AffaireType, default="C", max_length = 12, verbose_name = "Type d'Affaire", blank = True)
    ID_Pilote = models.ForeignKey(Pilote, on_delete=models.SET_NULL, verbose_name = "Pilote", blank = True, null = True)
    Etat = models.CharField(choices = EtatAffaireType, max_length = 8, verbose_name = "Etat de l'Affaire", default = "EC", blank = True)

    def custom_delete(self):
        if self.Etat != 'EC':
            self.delete()

    def get_absolute_url(self):
        return reverse('admin : bdd_Affaire_change', kwargs={'pk': self.pk})

    def __str__(self):
        return "{} , {} ".format(self.Nom_Affaire,self.Ref_Affaire)

    def Affiche_Reste_A_Regler(self):
        nombre = self.Reste_A_Regler()
        return '{:,.2f}'.format(nombre).replace(',', ' ').replace('.', ',')

    Affiche_Reste_A_Regler.short_description = "Reste à facturer"

    class Meta:
        ordering = ['Nom_Affaire']

    def Descriptif(self):
        mission = Offre_Mission.objects.get(pk=self.ID_Mission_id)
        descriptif = mission.Descriptif
        return descriptif

    def Adresse(self):
        mission = Offre_Mission.objects.get(pk=self.ID_Mission_id)
        adresse = mission.Adresse
        return adresse

    def CP(self):
        ID = self.ID_Mission_id
        mission = Offre_Mission.objects.get(pk=ID)
        cp = mission.CP
        return cp

    def Ville(self):
        ID = self.ID_Mission_id
        mission = Offre_Mission.objects.get(pk=ID)
        ville = mission.Ville
        return ville

    Adresse.short_description = "Adresse de la Mission"
    CP.short_description = "Code Postal"
    Ville.short_description = "Ville"

    def creer_previsionnel(self):
        idaffaire = self.pk
        dateprevisionnelle = self.Date_Previsionnelle
        if dateprevisionnelle == None:
            dateprevisionnelle = date.today()
            #self.Date_Previsionnelle = dateprevisionnelle
        montant = self.Honoraires_Global
        previsionnel = Previsionnel.objects.create(ID_Affaire_id = idaffaire,Date_Previsionnelle1 = dateprevisionnelle,
                                                   Montant_Previsionnel1 = montant)
        previsionnel.save()
        self.previsionnelcree = True
        self.save()

    def id_previsionnel(self):
        idaffaire = self.pk
        previsionnel = Previsionnel.objects.get(ID_Affaire_id = idaffaire)
        idprev = previsionnel.pk
        return idprev

    def Premiere_Date_Previsionnelle(self):
        try:
            idaffaire = self.pk
            previsionnel = Previsionnel.objects.get(ID_Affaire_id=idaffaire)
            date = previsionnel.Date_Previsionnelle_En_Cours()
        except:
            date = self.Date_Previsionnelle
        return date

    Premiere_Date_Previsionnelle.short_description = "Première Date Prévisionnelle de Facturation"

    def save(self, *args,**kwargs):
        if self.Ref_Affaire == 'A0001':  #Lors de la création de l'affaire, création du numéro, accepation de l'offre, remplissage automatique des champs connus
            aujourdhui = date.today()
            annee = aujourdhui.year
            mois = aujourdhui.month
            periode = '{}{:02d}'.format(annee,mois)
            indice = calcul_indice('A', periode)
            self.Ref_Affaire = 'A-{}{:04d}'.format(periode,indice)
            self.Indice_Dossier = indice
            mission = Offre_Mission.objects.get(pk=self.ID_Mission_id)
            mission.Etat = "ACC"
            mission.Date_Acceptation = aujourdhui
            mission.save()
            self.ID_Payeur = mission.ID_Payeur
            self.ID_Client_Cache = mission.ID_Client_Cache
            self.Nom_Affaire = mission.Nom_Mission
            self.Honoraires_Global = mission.Honoraires_Proposes
            self.ID_Pilote = mission.ID_Pilote
        else:
            if self.soldee:
                self.Etat = 'ARC'
            if not self.soldee:
                self.Etat = 'EC'
            if self.ID_Envoi_Facture == None and self.ID_Payeur != None and self.Ref_Affaire != 'A0001':
                envoi_facture = creer_Envoi_Facture(self.ID_Payeur_id)
                idenvoifacture = envoi_facture.id
                self.ID_Envoi_Facture_id = idenvoifacture

        super().save(*args,**kwargs)

    def client(self):
        mission = Offre_Mission.objects.get(pk=self.ID_Mission_id)
        client = mission.ID_Client_Cache
        return client

    def Reste_A_Regler(self):
        ID = self.id
        resultat = Facture.objects.filter(ID_Affaire = ID).filter(deja_validee=True).aggregate(deja_regle = Sum('Montant_Facture_HT'))['deja_regle'] or 0
        reste = self.Honoraires_Global - resultat
        return reste

    Reste_A_Regler.short_description = "Reste à facturer"

    def Solde(self):
        ID = self.id
        resultat = Facture.objects.filter(ID_Affaire=ID).filter(deja_payee=True).aggregate(deja_regle=Sum('Montant_Facture_HT'))[
                       'deja_regle'] or 0
        reste = self.Honoraires_Global - resultat
        return reste

    Solde.short_description = "Reste à Payer"

    class Meta:
        verbose_name_plural = "2. Affaires"

class Previsionnel(models.Model):
    ID_Affaire = models.OneToOneField(Affaire , on_delete=models.CASCADE, verbose_name = "Nom de l'affaire")
    Date_Previsionnelle1 = models.DateField(blank = True, null = True, default = None, verbose_name = "Date prévisionnelle 1 de facturation")
    Date_Previsionnelle2 = models.DateField(blank=True, null=True, default=None,
                                           verbose_name="Date prévisionnelle 2 de facturation")
    Date_Previsionnelle3 = models.DateField(blank=True, null=True, default=None,
                                           verbose_name="Date prévisionnelle 3 de facturation")
    Date_Previsionnelle4 = models.DateField(blank=True, null=True, default=None,
                                           verbose_name="Date prévisionnelle 4 de facturation")
    Date_Previsionnelle5 = models.DateField(blank=True, null=True, default=None,
                                           verbose_name="Date prévisionnelle 5 de facturation")
    Date_Previsionnelle6 = models.DateField(blank=True, null=True, default=None,
                                           verbose_name="Date prévisionnelle 6 de facturation")
    Date_Previsionnelle7 = models.DateField(blank=True, null=True, default=None,
                                           verbose_name="Date prévisionnelle 7 de facturation")
    Montant_Previsionnel1 = models.DecimalField(max_digits=12, decimal_places=2, verbose_name = 'Montant prévisionnel 1', default = 0)
    Montant_Previsionnel2 = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Montant prévisionnel 2',
                                                default=0,blank=True)
    Montant_Previsionnel3 = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Montant prévisionnel 3',
                                                default=0,blank=True)
    Montant_Previsionnel4 = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Montant prévisionnel 4',
                                                default=0,blank=True)
    Montant_Previsionnel5 = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Montant prévisionnel 5',
                                                default=0,blank=True)
    Montant_Previsionnel6 = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Montant prévisionnel 6',
                                                default=0,blank=True)
    Montant_Previsionnel7 = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Montant prévisionnel 7',
                                                default=0,blank=True)

    def aujourdhui(self):
        return date.today()

    def fonction0(self):
        debut, fin = debut_fin_mois(self.aujourdhui(), 0)
        return self.Anterieur_Date(fin)
    def fonction1(self):
        debut, fin = debut_fin_mois(self.aujourdhui(), 1)
        return self.Montant_Entre_Date(debut, fin)
    def fonction2(self):
        debut, fin = debut_fin_mois(self.aujourdhui(), 2)
        return self.Montant_Entre_Date(debut, fin)
    def fonction3(self):
        debut, fin = debut_fin_mois(self.aujourdhui(), 3)
        return self.Montant_Entre_Date(debut, fin)
    def fonction4(self):
        debut, fin = debut_fin_mois(self.aujourdhui(), 4)
        return self.Montant_Entre_Date(debut, fin)
    def fonction5(self):
        debut, fin = debut_fin_mois(self.aujourdhui(), 5)
        return self.Montant_Entre_Date(debut, fin)
    def fonction6(self):
        debut, fin = debut_fin_mois(self.aujourdhui(), 6)
        return self.Montant_Entre_Date(debut, fin)
    def fonction7(self):
        debut, fin = debut_fin_mois(self.aujourdhui(), 7)
        return self.Montant_Entre_Date(debut, fin)
    def fonction8(self):
        debut, fin = debut_fin_mois(self.aujourdhui(), 8)
        return self.Montant_Entre_Date(debut, fin)
    def fonction9(self):
        debut, fin = debut_fin_mois(self.aujourdhui(), 9)
        return self.Montant_Entre_Date(debut, fin)
    def fonction10(self):
        debut, fin = debut_fin_mois(self.aujourdhui(), 10)
        return self.Montant_Entre_Date(debut, fin)
    def fonction11(self):
        debut, fin = debut_fin_mois(self.aujourdhui(), 11)
        return self.Montant_Entre_Date(debut, fin)
    def fonction12(self):
        debut, fin = debut_fin_mois(self.aujourdhui(), 12)
        return self.Montant_Entre_Date(debut, fin)
    def fonction13(self):
        debut, fin = debut_fin_mois(self.aujourdhui(), 13)
        return self.Posterieur_Date(debut)

    today = date.today()
    L, Ldescription = list_display_previsionnel(today)
    k = 0
    fonction0.short_description = Ldescription[k]
    k = 1
    fonction1.short_description = Ldescription[k]
    k = 2
    fonction2.short_description = Ldescription[k]
    k = 3
    fonction3.short_description = Ldescription[k]
    k = 4
    fonction4.short_description = Ldescription[k]
    k = 5
    fonction5.short_description = Ldescription[k]
    k = 6
    fonction6.short_description = Ldescription[k]
    k = 7
    fonction7.short_description = Ldescription[k]
    k = 8
    fonction8.short_description = Ldescription[k]
    k = 9
    fonction9.short_description = Ldescription[k]
    k = 10
    fonction10.short_description = Ldescription[k]
    k = 11
    fonction11.short_description = Ldescription[k]
    k = 12
    fonction12.short_description = Ldescription[k]
    k = 13
    fonction13.short_description = Ldescription[k]

    def Nom_Affaire(self):
        idaffaire = self.ID_Affaire_id
        affaire = Affaire.objects.get(pk = idaffaire)
        return affaire.Nom_Affaire

    def Descriptif(self):
        idaffaire = self.ID_Affaire_id
        affaire = Affaire.objects.get(pk = idaffaire)
        descriptif = affaire.Descriptif()
        return descriptif

    def Montant_Affaire(self):
        idaffaire = self.ID_Affaire_id
        affaire = Affaire.objects.get(pk = idaffaire)
        honoraires = affaire.Honoraires_Global
        return honoraires

    def Montant_Affaire_str(self):
        nombre = self.Montant_Affaire()
        return '{:,.2f}'.format(nombre).replace(',', ' ').replace('.', ',')
    Montant_Affaire_str.short_description = "Honoraires de l'Affaire"

    def Reste_A_Facturer(self):
        idaffaire = self.ID_Affaire_id
        affaire = Affaire.objects.get(pk=idaffaire)
        return affaire.Reste_A_Regler()

    def Reste_A_Facturer_str(self):
        nombre = self.Reste_A_Facturer()
        return '{:,.2f}'.format(nombre).replace(',', ' ').replace('.', ',')
    Reste_A_Facturer_str.short_description = "Reste à Facturer"

    def Deja_Facture(self):
        idaffaire = self.ID_Affaire_id
        affaire = Affaire.objects.get(pk=idaffaire)
        honoraires = affaire.Honoraires_Global
        resteafacturer = affaire.Reste_A_Regler()
        return honoraires - resteafacturer

    def Deja_Facture_str(self):
        nombre = self.Deja_Facture()
        return '{:,.2f}'.format(nombre).replace(',', ' ').replace('.', ',')
    Deja_Facture_str.short_description = "Déjà facturé"

    def Liste_Montants(self):
        L = [self.Montant_Previsionnel1, self.Montant_Previsionnel2, self.Montant_Previsionnel3, self.Montant_Previsionnel4,
             self.Montant_Previsionnel5, self.Montant_Previsionnel6, self.Montant_Previsionnel7]
        return L

    def Liste_Montant_Cumules(self):
        L = self.Liste_Montants()
        LC = [L[0]]
        montantcumule = L[0]
        for k in range(1,len(L)):
            if L[k] != None:
                montantcumule += L[k]
            else:
                montantcumule += 0
            LC.append(montantcumule)
        return LC

    def Liste_Montant_Non_Factures(self):
        Linit = self.Liste_Montants()
        LC = self.Liste_Montant_Cumules()
        k = self.Echeance_En_Cours()-1
        LNonFacture = []
        for i in range(k):
            LNonFacture.append(0)
        valk = LC[k] - self.Deja_Facture()
        LNonFacture.append(valk)
        for i in range(k+1,len(Linit)):
            LNonFacture.append(Linit[i])
        return LNonFacture

    def Reste(self):
        idaffaire = self.ID_Affaire_id
        affaire = Affaire.objects.get(pk = idaffaire)
        honoraires = affaire.Honoraires_Global
        montant = 0
        Lmontant = self.Liste_Montants()
        for x in Lmontant:
            if x !=None:
                montant += x
        reste = honoraires - montant
        return reste

    def Dernier_Montant_Non_Nul(self):
        #Renvoie le numéro (pas l'indice dans L) du dernier montant non nul, 7 si aucun montant n'est non nul.
        L = self.Liste_Montants()
        for i in range(1,len(L)):
            if L[i] == 0:
                return i
        return len(L)

    def Echeance_En_Cours(self): #Renvoie k+1 tel que LC[k] <= dejaregle < LC[k+1]
        #si ça renvoie 1 ça veut dire que, compte tenu des factures déjà créées,
        #la phase en cours est DateEcheance1 avec MontantEcheance1
        LC = self.Liste_Montant_Cumules()
        idaffaire = self.ID_Affaire_id
        affaire = Affaire.objects.get(pk=idaffaire)
        restefacturer = affaire.Reste_A_Regler()
        dejaregle = affaire.Honoraires_Global - restefacturer
        k = 0
        while k < len(LC) and dejaregle >= LC[k]:
            if dejaregle >= LC[k]:
                k += 1
        if k < 7:
            return k + 1
        elif k==7:
            return 7

    Echeance_En_Cours.short_description = "Numéro Phase Prévisionnelle en Cours"

    def Liste_Dates(self):
        L = [self.Date_Previsionnelle1, self.Date_Previsionnelle2, self.Date_Previsionnelle3, self.Date_Previsionnelle4,
             self.Date_Previsionnelle5, self.Date_Previsionnelle6, self.Date_Previsionnelle7]
        return L

    def Montant_Entre_Date(self,date1,date2):
        LMontant = self.Liste_Montant_Non_Factures()
        Ldate = self.Liste_Dates()
        total = 0
        for k in range(len(LMontant)):
            montant = LMontant[k]
            date = Ldate[k]
            if date != None and date1 <= date <= date2:
                total += montant
        return total

    def Posterieur_Date(self,date1):
        LMontant = self.Liste_Montant_Non_Factures()
        Ldate = self.Liste_Dates()
        total = 0
        for k in range(len(LMontant)):
            montant = LMontant[k]
            date = Ldate[k]
            if date != None and date1 <= date:
                total += montant
        return total

    def Anterieur_Date(self,date2):
        LMontant = self.Liste_Montant_Non_Factures()
        Ldate = self.Liste_Dates()
        total = 0
        for k in range(len(LMontant)):
            montant = LMontant[k]
            date = Ldate[k]
            if date != None and date <= date2:
                total += montant
        return total

    def Montant_Mois(self,mois,annee):
        date1 = date(annee,mois,1)
        date2 = date(annee,mois,30)
        return self.Montant_Entre_Date(date1,date2)

    def Date_Previsionnelle_En_Cours(self):
        k = self.Echeance_En_Cours()
        L = self.Liste_Dates()
        return L[k-1]

    def Montant_Max_Echeance_En_Cours(self):
        k = self.Echeance_En_Cours()
        LC = self.Liste_Montant_Cumules()
        dejaregle = self.Deja_Facture()
        montantmax = LC[k-1] - dejaregle
        return montantmax

    def Prochaine_Date_Previsionnelle(self):
        k = self.Echeance_En_Cours()
        L = self.Liste_Dates()
        #print(L)
        #print(k)
        if k<7:
            return L[k]
        else:
            return L[6]

    def Mise_A_Jour_Date(self,date):
        k = self.Echeance_En_Cours()
        if k == 1:
            self.Date_Previsionnelle1 = date
        elif k == 2:
            self.Date_Previsionnelle2 = date
        elif k == 3:
            self.Date_Previsionnelle3 = date
        elif k == 4:
            self.Date_Previsionnelle4 = date
        elif k == 5:
            self.Date_Previsionnelle5 = date
        elif k == 6:
            self.Date_Previsionnelle6 = date
        elif k == 7:
            self.Date_Previsionnelle7 = date
        self.save()

    def Mise_A_Jour_Montant(self):
        k = self.Dernier_Montant_Non_Nul()
        reste = self.Reste()
        if reste > 0:
            if k == 1:
                if self.Montant_Previsionnel2 != None:
                    self.Montant_Previsionnel2 += reste
                else:
                    self.Montant_Previsionnel2 = reste
                if self.Date_Previsionnelle2 == None:
                    self.Date_Previsionnelle2 = self.Date_Previsionnelle1
            elif k == 2:
                if self.Montant_Previsionnel3 != None:
                    self.Montant_Previsionnel3 += reste
                else:
                    self.Montant_Previsionnel3 = reste
                if self.Date_Previsionnelle3 == None:
                    self.Date_Previsionnelle3 = self.Date_Previsionnelle2
            elif k == 3:
                if self.Montant_Previsionnel4 != None:
                    self.Montant_Previsionnel4 += reste
                else:
                    self.Montant_Previsionnel4 = reste
                if self.Date_Previsionnelle4 == None:
                    self.Date_Previsionnelle4 = self.Date_Previsionnelle3
            elif k == 4:
                if self.Montant_Previsionnel5 != None:
                    self.Montant_Previsionnel5 += reste
                else:
                    self.Montant_Previsionnel5 = reste
                if self.Date_Previsionnelle5 == None:
                    self.Date_Previsionnelle5 = self.Date_Previsionnelle4
            elif k == 5:
                if self.Montant_Previsionnel6 != None:
                    self.Montant_Previsionnel6 += reste
                else:
                    self.Montant_Previsionnel6 = reste
                if self.Date_Previsionnelle6 == None:
                    self.Date_Previsionnelle6 = self.Date_Previsionnelle5
            elif k == 6:
                if self.Montant_Previsionnel7 != None:
                    self.Montant_Previsionnel7 += reste
                else:
                    self.Montant_Previsionnel7 = reste
                if self.Date_Previsionnelle7 == None:
                    self.Date_Previsionnelle7 = self.Date_Previsionnelle6
            elif k == 7:
                if self.Montant_Previsionnel7 != None:
                    self.Montant_Previsionnel8 += reste
                else:
                    self.Montant_Previsionnel7 = reste
            self.save()
        if reste < 0:
            if k == 1:
                if self.Montant_Previsionnel1 != None:
                    self.Montant_Previsionnel1 += reste
                else:
                    self.Montant_Previsionnel1 = reste
            elif k == 2:
                if self.Montant_Previsionnel2 != None:
                    self.Montant_Previsionnel2 += reste
                else:
                    self.Montant_Previsionnel2 = reste
            elif k == 3:
                if self.Montant_Previsionnel3 != None:
                    self.Montant_Previsionnel3 += reste
                else:
                    self.Montant_Previsionnel3 = reste
            elif k == 4:
                if self.Montant_Previsionnel4 != None:
                    self.Montant_Previsionnel4 += reste
                else:
                    self.Montant_Previsionnel4 = reste
            elif k == 5:
                if self.Montant_Previsionnel5 != None:
                    self.Montant_Previsionnel5 += reste
                else:
                    self.Montant_Previsionnel5 = reste
            elif k == 6:
                if self.Montant_Previsionnel6 != None:
                    self.Montant_Previsionnel6 += reste
                else:
                    self.Montant_Previsionnel6 = reste
            elif k == 7:
                if self.Montant_Previsionnel7 != None:
                    self.Montant_Previsionnel7 += reste
                else:
                    self.Montant_Previsionnel7 = reste
            self.save()
        k = self.Dernier_Montant_Non_Nul()
        Lmontant = self.Liste_Montants()
        if Lmontant[k-1] < 0:
            if k == 1:
                self.Montant_Previsionnel1 = 0
            elif k == 2:
                self.Montant_Previsionnel2 = 0
            elif k == 3:
                self.Montant_Previsionnel3 = 0
            elif k == 4:
                self.Montant_Previsionnel4 = 0
            elif k == 5:
                self.Montant_Previsionnel5 = 0
            elif k == 6:
                self.Montant_Previsionnel6 = 0
            elif k == 7:
                self.Montant_Previsionnel7 = 0
            self.save()
            self.Mise_A_Jour_Montant()

    def save(self, *args, **kwargs):
        if self.Montant_Previsionnel1 == None:
            self.Montant_Previsionnel1 = 0
        if self.Montant_Previsionnel2 == None:
            self.Montant_Previsionnel2 = 0
        if self.Montant_Previsionnel3 == None:
            self.Montant_Previsionnel3 = 0
        if self.Montant_Previsionnel4 == None:
            self.Montant_Previsionnel4 = 0
        if self.Montant_Previsionnel5 == None:
            self.Montant_Previsionnel5 = 0
        if self.Montant_Previsionnel6 == None:
            self.Montant_Previsionnel6 = 0
        if self.Montant_Previsionnel7 == None:
            self.Montant_Previsionnel7 = 0
        affaire = Affaire.objects.get(id=self.ID_Affaire_id)
        affaire.Date_Previsionnelle = self.Date_Previsionnelle_En_Cours()
        affaire.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "7. Previsionnel"

class Facture(models.Model):
    deja_validee = models.BooleanField(default = False, verbose_name = 'Validée') #Pour savoir si la facture a déjà été validée
    deja_envoyee = models.BooleanField(default = False, verbose_name = 'Envoyée') #Pour savoir si la facture a déjà été envoyée par mail
    deja_payee = models.BooleanField(default = False, verbose_name = 'Payée')  #Pour savoir si la facture a été payée ou non

    Numero_Facture = models.CharField(default = "",max_length = 50, verbose_name = "Numéro de facture", blank = True)
    Indice_Facture = models.IntegerField(default = 0,blank=True)
    ID_Affaire  = models.ForeignKey(Affaire , on_delete=models.CASCADE, verbose_name = "Nom de l'affaire")
    ID_Prev = models.ForeignKey(Previsionnel , on_delete=models.SET_NULL, verbose_name = "Prévisionnel de l'affaire", null = True, blank = True)
    Nom_Affaire = models.CharField(max_length = 100, verbose_name = "Nom de l'Affaire", blank = True, null = True)
    ID_Payeur = models.ForeignKey(Client,on_delete=models.SET_NULL, null = True,verbose_name = "Payeur")
    ID_Envoi_Facture = models.ForeignKey(Envoi_Facture, on_delete=models.CASCADE,
                                         verbose_name="Adresse d'envoi de la facture", null = True)
    Ref_Client = models.CharField(max_length=150,blank = True, verbose_name="Référence Client à rappeler")
    ID_Pilote = models.ForeignKey(Pilote, on_delete=models.SET_NULL, null = True, verbose_name = "Pilote")

    Descriptif = models.TextField()
    Montant_Facture_HT = models.DecimalField(max_digits=12, decimal_places=2, verbose_name = 'Montant Facture H.T.', default = 0)
    Taux_TVA = models.CharField(choices = TVA, max_length = 2, verbose_name = "Taux de T.V.A.", default = "20")

    Date_Facture = models.DateField(default=date.today, verbose_name = "Date de la facture")

    Facture_Avoir = models.CharField(choices = FactureType, max_length = 10, verbose_name = "Facture ou Avoir", default = "FA")
    Facture_Liee = models.CharField(max_length=20, null=True, blank=True, verbose_name="Facture liée")  # Numéro de la facture liée à l'avoir
    #Avoir_Lie = models.CharField(max_length=20, null=True, blank=True,verbose_name="Avoir lié")  #Numéro de l'avoir lié à la facture si existe

    Etat = models.CharField(choices = EtatFacture, max_length = 8, verbose_name = "Etat", default = "BR")
    Etat_Paiement = models.CharField(choices = EtatPaiement, max_length = 8, verbose_name = "Etat du paiement", default = "ATT",blank = True)
    Date_Envoi = models.DateField(default=date.today, verbose_name="Date d'envoi", blank=True)
    Date_Relance1 = models.DateField(default=date.today, verbose_name="Date de relance1 - relance par mail - J", blank=True)
    Date_Relance2 = models.DateField(default=date.today, verbose_name="Date de relance2 - relance courrier suivi - J+30", blank=True)
    Date_Relance3 = models.DateField(default=date.today, verbose_name="Date de relance3 - relance RAR - J+60", blank=True)
    Date_Relance4 = models.DateField(default=date.today, verbose_name="Date de relance4 - nise en demeure - J+90", blank=True)
    Date_Relance5 = models.DateField(default=date.today, verbose_name="Date de relance5 - conciliation - J+100", blank=True)
    Date_Relance6 = models.DateField(default=date.today, verbose_name="Date de relance6 - assignation - J+220", blank=True)
    Date_Dernier_Rappel = models.DateField(default=date.today, verbose_name = "Date dernier rappel", blank = True)
    Num_Relance = models.IntegerField(default = 0, blank = True)
    Num_Suivi = models.CharField(max_length = 20, blank = True, default = 'A préciser', verbose_name = "Numéro Suivi - Relance2") #Numéro du RAR de la relance 2
    Num_RAR = models.CharField(max_length = 25, blank = True, default = 'A préciser', verbose_name = "Numéro RAR - Relance3") #Numéro du RAR de la relance 3
    Num_RAR_Demeure = models.CharField(max_length = 25, blank = True, default = 'A préciser', verbose_name = "Numéro RAR - Relance4 (Mise en demeure)") #Numéro du RAR de la mise en demeure

    Mode_Paiement = models.CharField(default="Non défini", choices=ModePaiementType, max_length=20,
                                     verbose_name="Mode de Paiement")
    Delais_Paiement = models.IntegerField(default=30, verbose_name="Délais de Paiement (en jours)")
    Fin_Mois = models.CharField(choices=OuiOuNonType.choices, max_length=3, default="Non", verbose_name="Fin de Mois")
    Modalites_Paiement = models.TextField(blank=True, verbose_name="Modalités particulières de Paiement")

    Denomination_Client = models.CharField(max_length=50, verbose_name="Dénomination sociale Client")
    Adresse_Client = models.CharField(max_length=500, blank=True)
    Complement_Adresse_Client = models.CharField(max_length=500, blank=True)
    CP_Client = models.CharField(validators=[CP_regex], max_length=5, verbose_name='Code postal', blank=True)
    Ville_Client = models.CharField(max_length=150, blank=True)
    Civilite_Client = models.CharField(blank=True, choices=CiviliteType.choices, max_length=3, verbose_name = "Civilité")
    Nom_Client = models.CharField(max_length=50, blank=True, verbose_name="Nom")
    Prenom_Client = models.CharField(max_length=50, blank=True, verbose_name="Prénom")
    Email_Client = models.EmailField(max_length=70, blank=True, verbose_name="Email")

    Denomination_Facture = models.CharField(max_length=50, verbose_name="Dénomination sociale Facture")
    Adresse_Facture = models.CharField(max_length=500)
    Complement_Adresse_Facture = models.CharField(max_length=500, blank=True)
    CP_Facture = models.CharField(validators=[CP_regex], max_length=5, verbose_name='Code postal')
    Ville_Facture = models.CharField(max_length=150)
    Civilite_Facture = models.CharField(blank=True, choices=CiviliteType.choices, max_length=3)
    Nom_Facture = models.CharField(max_length=50, blank=True, verbose_name="Nom")
    Prenom_Facture = models.CharField(max_length=50, blank=True, verbose_name="Prénom")
    Email_Facture = models.EmailField(max_length=70, blank=True, verbose_name='Email')

    Civilite_Pilote = models.CharField(blank=True, choices=CiviliteType.choices, max_length=3)
    Nom_Pilote = models.CharField(max_length=50, blank=True)
    Prenom_Pilote = models.CharField(max_length=50, blank=True)
    Tel_Portable_Pilote = models.CharField(validators=[tel_regex], max_length=16, verbose_name='Numéro de Portable',
                                    blank=True)
    Email_Pilote = models.EmailField(max_length=70, blank=True)

    Nom_Fichier_Facture = models.CharField(max_length=300,blank=True,verbose_name="Nom du fichier Facture")
    Fichier_Facture_cree = models.BooleanField(default=False, verbose_name="Facture_pdf_créée")
    Date_Creation_Fichier_Facture = models.DateTimeField(null=True, blank=True, verbose_name="Date de création du fichier facture pdf")
    Nom_Fichier_Relance2 = models.CharField(max_length=300, blank=True, verbose_name="Nom du fichier Relance2")
    Fichier_Relance2_cree = models.BooleanField(default=False, verbose_name="Relance2_pdf_créée")
    Date_Creation_Fichier_Relance2 = models.DateTimeField(null=True, blank=True, verbose_name="Date de création du fichier relance2 pdf")
    Nom_Fichier_Relance3 = models.CharField(max_length=300, blank=True, verbose_name="Nom du fichier Relance3")
    Fichier_Relance3_cree = models.BooleanField(default=False, verbose_name="Relance3_pdf_créée")
    Date_Creation_Fichier_Relance3 = models.DateTimeField(null=True, blank=True, verbose_name="Date de création du fichier relance3 pdf")
    Nom_Fichier_Relance4 = models.CharField(max_length=300, blank=True, verbose_name="Nom du fichier Relance4")
    Fichier_Relance4_cree = models.BooleanField(default=False, verbose_name="Relance4_pdf_créée")
    Date_Creation_Fichier_Relance4 = models.DateTimeField(null=True, blank=True, verbose_name="Date de création du fichier relance4 pdf")

    #Pour les fichiers de relance word téléversés
    Fichier_Word_cree = models.BooleanField(default=False, verbose_name="Fichiers Words Créés")

    class Meta:
        verbose_name_plural = "3. Factures"

    def id_fichier_word(self):
        idfacture = self.pk
        fichier_word = Fichier_Word.objects.get(ID_Facture_id = idfacture)
        idfichierword = fichier_word.pk
        return idfichierword

    def creer_fichier_word(self):  #Pour créer l'enregistrement associé dans Fichier_Word
        idfacture = self.pk
        fichier_word = Fichier_Word.objects.create(ID_Facture_id = idfacture)
        fichier_word.save()
        self.Fichier_Word_cree = True
        self.save()

    def id_previsionnel(self):
        idaffaire = self.ID_Affaire_id
        affaire = Affaire.objects.get(pk=idaffaire)
        if not affaire.previsionnelcree:
            affaire.creer_previsionnel()
        previsionnel = Previsionnel.objects.get(ID_Affaire_id = idaffaire)
        idprev = previsionnel.pk
        return idprev

    def pdf(self):
        if not self.deja_validee:
            return None
        elif not self.Fichier_Facture_cree:
            return None
        else:
            return mark_safe("<a href='%s' target='_blank'>PDF</a>"%reverse('facture_pdf',args=[self.id]))

    def word(self):
        return mark_safe("<a href='%s' target='_blank'>WORD</a>"%reverse('relance_word2', args=[self.id]))

    def relance2_word(self):
        #chargement des données
        facture = self
        ingeprev = Ingeprev.objects.get(Nom='INGEPREV')
        affaire = Affaire.objects.get(pk = self.ID_Affaire_id)
        mission = Offre_Mission.objects.get(pk=affaire.ID_Mission_id)
        payeur = Client.objects.get(pk = self.ID_Payeur_id)
        envoi = Envoi_Facture.objects.get(pk = self.ID_Envoi_Facture_id)
        doc = relance_word(2,facture,ingeprev, affaire, mission, payeur, envoi)
        return doc
    def relance3_word(self):
        #chargement des données
        facture = self
        ingeprev = Ingeprev.objects.get(Nom='INGEPREV')
        affaire = Affaire.objects.get(pk = self.ID_Affaire_id)
        mission = Offre_Mission.objects.get(pk=affaire.ID_Mission_id)
        payeur = Client.objects.get(pk = self.ID_Payeur_id)
        envoi = Envoi_Facture.objects.get(pk = self.ID_Envoi_Facture_id)
        doc = relance_word(3,facture,ingeprev, affaire, mission, payeur, envoi)
        return doc
    def relance4_word(self):
        #chargement des données
        facture = self
        ingeprev = Ingeprev.objects.get(Nom='INGEPREV')
        affaire = Affaire.objects.get(pk = self.ID_Affaire_id)
        mission = Offre_Mission.objects.get(pk=affaire.ID_Mission_id)
        payeur = Client.objects.get(pk = self.ID_Payeur_id)
        envoi = Envoi_Facture.objects.get(pk = self.ID_Envoi_Facture_id)
        doc = relance_word(4,facture,ingeprev, affaire, mission, payeur, envoi)
        return doc

    def Date_Facture_aff(self):
        return self.Date_Facture.strftime('%d/%m/%Y')
    def Date_Echeance1_aff(self):
        return self.Date_Echeance1().strftime('%d/%m/%Y')
    def Date_Relance1_aff(self):
        return self.Date_Relance1.strftime('%d/%m/%Y')
    def Date_Relance2_aff(self):
        return self.Date_Relance2.strftime('%d/%m/%Y')
    def Date_Relance3_aff(self):
        return self.Date_Relance3.strftime('%d/%m/%Y')

    def Fonction_Nom_Fichier_Facture(self):
        chemin = Path(DOSSIER_PRIVE + 'factures/{}.pdf'.format(self.Numero_Facture))
        return chemin
    def Fonction_Nom_Fichier_Word_Relance(self,k):
        chemin = Path(DOSSIER_PRIVE + 'relances/Relance{}-{}.docx'.format(k,self.Numero_Facture))
        return chemin
    def Fonction_Nom_Fichier_Pdf_Relance(self,k):
        chemin = Path(DOSSIER_PRIVE + 'relances/Relance{}-{}.pdf'.format(k,self.Numero_Facture))
        return chemin

    def Word2Cree(self):
        try:
            fichier_word = Fichier_Word.objects.get(ID_Facture_id=self.id)
            return fichier_word.Word2_cree
        except:
            return False
    def Word3Cree(self):
        try:
            fichier_word = Fichier_Word.objects.get(ID_Facture_id=self.id)
            return fichier_word.Word3_cree
        except:
            return False
    def Word4Cree(self):
        try:
            fichier_word = Fichier_Word.objects.get(ID_Facture_id=self.id)
            return fichier_word.Word4_cree
        except:
            return False

    def Tel_Portable_Pilote_Affiche(self):
        return formater_tel(self.Tel_Portable_Pilote)

    def custom_delete(self):
        if not self.deja_validee:
            self.delete()
        else:
            pass

    def Avoirs_Lies(self):
        L = []
        qs = Facture.objects.filter(Facture_Liee=self.Numero_Facture).filter(deja_validee=True)
        for avoir in qs:
            if avoir.deja_validee:
                L.append(avoir.Numero_Facture)
        return L

    Avoirs_Lies.short_description = 'Avoirs liés'

    def Montants_Avoirs_Lies(self):
        L = []
        qs = Facture.objects.filter(Facture_Liee=self.Numero_Facture).filter(deja_validee=True)
        for avoir in qs:
            if avoir.deja_validee:
                val = avoir.Montant_Facture_HT
                affiche = '{:,.2f}'.format(val).replace(',', ' ').replace('.', ',')
                L.append(affiche)
        return L

    Montants_Avoirs_Lies.short_description = 'Montants Avoirs liés'

    def Montants_Avoirs_Lies_TTC(self):
        L = []
        qs = Facture.objects.filter(Facture_Liee=self.Numero_Facture).filter(deja_validee=True)
        for avoir in qs:
            if avoir.deja_validee:
                L.append(avoir.Montant_Facture_TTC())
        return L

    def Somme_Avoirs_Lies(self):
        s = Decimal('0.00')
        qs = Facture.objects.filter(Facture_Liee=self.Numero_Facture).filter(deja_validee=True)
        for avoir in qs:
            if avoir.deja_validee:
                s += avoir.Montant_Facture_HT
        return s

    def Date_Facture_Liee(self):
        qs = Facture.objects.filter(Numero_Facture = self.Facture_Liee)
        date = None
        for facture in qs:
            date = facture.Date_Facture
        return date

    def Nb_Avoir(self):  #nb d'avoirs liés à la facture et validés
        nb = 0
        qs = Facture.objects.filter(Facture_Liee=self.Numero_Facture)
        for avoir in qs:
            if avoir.deja_validee:
                nb += 1
        return nb

    def Solde_Pour_Avoir_Eventuel(self):
        montantfacture = self.Montant_Facture_HT
        reste = montantfacture
        L_Avoirs_Lies_Valides = self.Avoirs_Lies()
        for num in L_Avoirs_Lies_Valides:
            for avoir in Facture.objects.filter(Numero_Facture=num):
                if avoir.deja_validee:
                    montantavoir = avoir.Montant_Facture_HT
                    reste += montantavoir
        return reste

    Solde_Pour_Avoir_Eventuel.short_description = "Montant disponible pour avoirs éventuels."

    def Reste_A_Payer(self): #Montant restant de la facture initiale, avoirs payés déduits
        montantfacture = self.Montant_Facture_HT
        reste = montantfacture
        L_Avoirs_Lies_Valides = self.Avoirs_Lies()
        for num in L_Avoirs_Lies_Valides:
            for avoir in Facture.objects.filter(Numero_Facture=num):
                if avoir.deja_payee:
                    montantavoir = avoir.Montant_Facture_HT
                    reste += montantavoir
        if self.Facture_Avoir == 'AV' and self.deja_payee:
            reste = Decimal('0.00')
        return reste

    Reste_A_Payer.short_description = "Montant Avoirs Payés Déduits"

    def Reste_A_Payer_TTC(self):
        reste = self.Reste_A_Payer()
        return reste*(100+int(self.Taux_TVA))/100

    def Montant_Facture_TTC(self):
        return self.Montant_Facture_HT * (100+int(self.Taux_TVA))/100

    def save(self,*args,**kwargs):
        if self.Numero_Facture == '':  #Lors de la création de la facture = remplissage automatique des champs connus
            affaire = Affaire.objects.get(pk=self.ID_Affaire_id)
            self.ID_Payeur = affaire.ID_Payeur
            self.Nom_Affaire = affaire.Nom_Affaire
            self.ID_Envoi_Facture = affaire.ID_Envoi_Facture
            self.ID_Pilote = affaire.ID_Pilote
            self.Ref_Client=affaire.Ref_Client
            self.Numero_Facture = 'FA0001'
            self.save()
        if not self.deja_validee or not self.deja_envoyee:
            self.deja_payee = False
        if self.deja_payee:
            self.Etat_Paiement = 'PAYE'
        if not self.deja_payee:
            self.Etat_Paiement = 'ATT'
        affaire = Affaire.objects.get(pk=self.ID_Affaire_id)   #Mise à jour de l'affaire en cas de modifs lors de la facture
        affaire.ID_Envoi_Facture = self.ID_Envoi_Facture
        affaire.ID_Pilote = self.ID_Pilote
        affaire.Ref_Client = self.Ref_Client
        affaire.save()
        if self.Facture_Avoir == "AV" and self.deja_envoyee:
            self.deja_payee=True
            self.Etat_Paiement="PAYE"
            num = self.Facture_Liee
            qs = Facture.objects.filter(Numero_Facture=num)
            if qs.count() >= 1:
                facture = Facture.objects.get(Numero_Facture=num)
                if abs(facture.Reste_A_Payer()) < 10 ** (-2):
                    facture.deja_payee = True
                    facture.Etat_Paiement = 'PAYE'
                facture.save()
        if self.Facture_Avoir == "FA" and self.Reste_A_Payer()<10**(-2) and self.deja_envoyee:
            self.deja_payee=True
            self.Etat_Paiement='PAYE'
        super().save(*args,**kwargs)

    def Reste_Affaire(self):
        affaire = Affaire.objects.get(pk = self.ID_Affaire_id)
        reste = affaire.Reste_A_Regler()
        return '{:,.2f}'.format(reste).replace(',', ' ').replace('.', ',')

    def Valeur_Reste_Affaire(self):
        affaire = Affaire.objects.get(pk = self.ID_Affaire_id)
        reste = affaire.Reste_A_Regler()
        return reste

    def Honoraire_Affaire(self):
        affaire = Affaire.objects.get(pk=self.ID_Affaire_id)
        honoraire = affaire.Honoraires_Global
        return '{:,.2f}'.format(honoraire).replace(',', ' ').replace('.', ',')

    def Date_Prev_Affaire(self):
        affaire = Affaire.objects.get(pk=self.ID_Affaire_id)
        return affaire.Date_Previsionnelle

    def Date_Prev_Affaire_aff(self):
        return self.Date_Prev_Affaire().strftime('%d/%m/%Y')

    Date_Prev_Affaire_aff.short_description = "Date prévisionnelle actuelle de l'affaire"

    def Date_Prev_En_Cours_Affaire(self):
        try:
            previsionnel = Previsionnel.objects.get(ID_Affaire=self.ID_Affaire_id)
            return previsionnel.Date_Previsionnelle_En_Cours()
        except:  #cas où le prévisionnel n'a pas encore été créé
            affaire = Affaire.objects.get(pk=self.ID_Affaire_id)
            return affaire.Date_Previsionnelle

    def Date_Prev_En_Cours_Affaire_aff(self):
        return self.Date_Prev_En_Cours_Affaire().strftime('%d/%m/%Y')

    Date_Prev_En_Cours_Affaire_aff.short_description = "Date prévisionnelle actuelle de l'affaire"

    def Num_Affaire(self):
        affaire = Affaire.objects.get(pk=self.ID_Affaire_id)
        return affaire.Ref_Affaire

    def Envoi_Facture_Affaire(self):
        affaire = Affaire.objects.get(pk=self.ID_Affaire_id)
        return affaire.ID_Envoi_Facture

    def Client_Cache(self):
        affaire = Affaire.objects.get(pk=self.ID_Affaire_id)
        return affaire.client()

    def Date_Echeance1(self):
        if self.Fin_Mois == "Non":
            echeance = self.Date_Facture + timedelta(days=self.Delais_Paiement)
        elif self.Fin_Mois == "Oui": #Ici on est forcément à 30 jours fin de mois
            datefacture = self.Date_Facture
            premier = datefacture + timedelta(30)
            debut,fin = debut_fin_mois(premier,0)
            echeance = fin
        return echeance

    def Date_Relance(self):
        dateecheance1 = self.Date_Echeance1()
        relance = self.Num_Relance
        daterelance = dateecheance1 + timedelta(days = 30*(relance-1))
        if relance == 5:
            daterelance = dateecheance1 + timedelta(days=100)
        elif relance == 6:
            daterelance = dateecheance1 + timedelta(days=220)
        elif relance == 0:
            daterelance = 'Facture non envoyée'
        return daterelance

    Reste_Affaire.short_description = "Montant de l'affaire qu'il reste à facturer"
    Honoraire_Affaire.short_description = "Montant honoraires de l'affaire"

    def Remplissage_Facture(self):
        payeur = Client.objects.get(pk=self.ID_Payeur_id)
        self.Denomination_Client = payeur.Denomination_Sociale
        self.Adresse_Client = payeur.Adresse
        self.Complement_Adresse_Client = payeur.Complement_Adresse
        self.CP_Client = payeur.CP
        self.Ville_Client = payeur.Ville
        self.Civilite_Client = payeur.Civilite
        self.Nom_Client = payeur.Nom_Representant
        self.Prenom_Client = payeur.Prenom_Representant
        self.Email_Client = payeur.Email_Representant
        pilote = Pilote.objects.get(pk=self.ID_Pilote_id)
        self.Civilite_Pilote = pilote.Civilite
        self.Nom_Pilote = pilote.Nom
        self.Prenom_Pilote = pilote.Prenom
        self.Email_Pilote = pilote.Email
        self.Tel_Portable_Pilote = pilote.Tel_Portable
        facture = Envoi_Facture.objects.get(pk=self.ID_Envoi_Facture_id)
        self.Denomination_Facture = facture.Denomination_Sociale
        self.Adresse_Facture = facture.Adresse
        self.Complement_Adresse_Facture = facture.Complement_Adresse
        self.CP_Facture = facture.CP
        self.Ville_Facture = facture.Ville
        self.Civilite_Facture = facture.Civilite
        self.Nom_Facture = facture.Nom_Contact
        self.Prenom_Facture = facture.Prenom_Contact
        self.Email_Facture = facture.Email_Contact
        self.Delais_Paiement = facture.Delais_Paiement
        self.Mode_Paiement = facture.Mode_Paiement
        self.Fin_Mois = facture.Fin_Mois
        self.Modalites_Paiement = facture.Modalites_Paiement
        if self.Montant_Facture_HT < 0:
            self.Facture_Avoir = 'AV'
        self.save()

    def Creation_Facture(self):
        self.save()
        aujourdhui = date.today()
        annee = aujourdhui.year
        mois = aujourdhui.month
        periode = '{}{:02d}'.format(annee, mois)
        indice = calcul_indice('FA', periode)
        self.Numero_Facture = 'FA-{}{:04d}'.format(periode, indice)
        self.Indice_Facture = indice
        payeur = Client.objects.get(pk=self.ID_Payeur_id)
        self.Denomination_Client = payeur.Denomination_Sociale
        self.Adresse_Client = payeur.Adresse
        self.Complement_Adresse_Client = payeur.Complement_Adresse
        self.CP_Client = payeur.CP
        self.Ville = payeur.Ville
        self.Civilite_Client = payeur.Civilite
        self.Nom_Client = payeur.Nom_Representant
        self.Prenom_Client = payeur.Prenom_Representant
        self.Email_Client = payeur.Email_Representant
        pilote = Pilote.objects.get(pk=self.ID_Pilote_id)
        self.Civilite_Pilote = pilote.Civilite
        self.Nom_Pilote = pilote.Nom
        self.Prenom_Pilote = pilote.Prenom
        self.Email_Pilote = pilote.Email
        self.Tel_Portable_Pilote = pilote.Tel_Portable
        facture = Envoi_Facture.objects.get(pk=self.ID_Envoi_Facture_id)
        self.Denomination_Facture = facture.Denomination_Sociale
        self.Adresse_Facture = facture.Adresse
        self.Complement_Adresse_Facture = facture.Complement_Adresse
        self.CP_Facture = facture.CP
        self.Ville_Facture = facture.Ville
        self.Civilite_Facture = facture.Civilite
        self.Nom_Facture = facture.Nom_Contact
        self.Prenom_Facture = facture.Prenom_Contact
        self.Email_Facture = facture.Email_Contact
        self.Delais_Paiement = facture.Delais_Paiement
        self.Mode_Paiement = facture.Mode_Paiement
        self.Fin_Mois = facture.Fin_Mois
        if self.Montant_Facture_HT < 0:
            self.Facture_Avoir = 'AV'
        self.save()

def renommage2(instance,nom_fichier):
    facture = Facture.objects.get(pk = instance.ID_Facture_id)
    numfacture = facture.Numero_Facture
    fichier = 'relances/Relance2-{}.docx'.format(numfacture)
    return fichier
def renommage3(instance,nom_fichier):
    facture = Facture.objects.get(pk = instance.ID_Facture_id)
    numfacture = facture.Numero_Facture
    fichier = 'relances/Relance3-{}.docx'.format(numfacture)
    return fichier
def renommage4(instance,nom_fichier):
    facture = Facture.objects.get(pk = instance.ID_Facture_id)
    numfacture = facture.Numero_Facture
    fichier = 'relances/Relance4-{}.docx'.format(numfacture)
    return fichier

def renommage2bis(instance,nom_fichier):
    facture = Facture.objects.get(pk = instance.ID_Facture_id)
    numfacture = facture.Numero_Facture
    fichier = 'relances/Relance2-{}.pdf'.format(numfacture)
    return fichier
def renommage3bis(instance,nom_fichier):
    facture = Facture.objects.get(pk = instance.ID_Facture_id)
    numfacture = facture.Numero_Facture
    fichier = 'relances/Relance3-{}.pdf'.format(numfacture)
    return fichier
def renommage4bis(instance,nom_fichier):
    facture = Facture.objects.get(pk = instance.ID_Facture_id)
    numfacture = facture.Numero_Facture
    fichier = 'relances/Relance4-{}.pdf'.format(numfacture)
    return fichier

class Fichier_Word(models.Model):
    ID_Facture = models.ForeignKey(Facture, on_delete=models.SET_NULL, verbose_name="Facture associée", blank=True,null=True)
    Word2 = models.FileField(upload_to=renommage2,blank=True,verbose_name="Fichier Word de Relance 2",default='')
    PDF2 = models.FileField(upload_to=renommage2bis, blank=True, verbose_name="Fichier PDF de Relance 2", default='')
    Word2_cree = models.BooleanField(default=False, verbose_name="Word2_créé")
    Date_Creation_Word2 = models.DateTimeField(null=True,blank=True, verbose_name="Date de création du Word2")
    Word3 = models.FileField(upload_to=renommage3, null=True, blank=True,verbose_name="Fichier Word de Relance 3",default='')
    PDF3 = models.FileField(upload_to=renommage3bis, blank=True, verbose_name="Fichier PDF de Relance 3", default='')
    Word3_cree = models.BooleanField(default=False, verbose_name="Word3_créé")
    Date_Creation_Word3 = models.DateTimeField(null=True,blank=True, verbose_name="Date de création du Word3")
    Word4 = models.FileField(upload_to=renommage4, blank=True,verbose_name="Fichier Word de Relance 4",default='')
    PDF4 = models.FileField(upload_to=renommage4bis, blank=True, verbose_name="Fichier PDF de Relance 4", default='')
    Word4_cree = models.BooleanField(default=False, verbose_name="Word4_créé")
    Date_Creation_Word4 = models.DateTimeField(null=True,blank=True, verbose_name="Date de création du Word4")

    def Fonction_Nom_Fichier_Word2(self):
        chemin = Path(DOSSIER_PRIVE + self.Word2.name)
        return chemin
    def Fonction_Nom_Fichier_Word3(self):
        chemin = Path(DOSSIER_PRIVE + self.Word3.name)
        return chemin
    def Fonction_Nom_Fichier_Word4(self):
        chemin = Path(DOSSIER_PRIVE + self.Word4.name)
        return chemin

    def lien_word2(self):
        if self.id == None:
            return None
        else:
            return mark_safe(
                "<a href='{}' target='_blank'>{}</a>".format(reverse('lien_fichier_word2', args=[self.id]), self.Word2))
    def lien_word3(self):
        if self.id == None:
            return None
        else:
            return mark_safe(
                "<a href='{}' target='_blank'>{}</a>".format(reverse('lien_fichier_word3', args=[self.id]), self.Word3))
    def lien_word4(self):
        if self.id == None:
            return None
        else:
            return mark_safe(
                "<a href='{}' target='_blank'>{}</a>".format(reverse('lien_fichier_word4', args=[self.id]), self.Word4))

    def lien_PDF2(self):
        if self.id == None:
            return None
        else:
            return mark_safe(
                "<a href='{}' target='_blank'>{}</a>".format(reverse('lien_fichier_pdf2', args=[self.id]), self.PDF2))
    def lien_PDF3(self):
        if self.id == None:
            return None
        else:
            return mark_safe(
                "<a href='{}' target='_blank'>{}</a>".format(reverse('lien_fichier_pdf3', args=[self.id]), self.PDF3))
    def lien_PDF4(self):
        if self.id == None:
            return None
        else:
            return mark_safe(
                "<a href='{}' target='_blank'>{}</a>".format(reverse('lien_fichier_pdf4', args=[self.id]), self.PDF4))

    def Numero_Facture(self):
        facture = Facture.objects.get(id = self.ID_Facture_id)
        return facture.Numero_Facture

    def creer_pdf(self,k):
        facture = Facture.objects.get(id = self.ID_Facture_id)
        if k == 2:
            source = self.Word2.path
            source_pdf = self.PDF2.path
        elif k == 3:
            source = self.Word3.path
            source_pdf = self.PDF3.path
        elif k == 4:
            source = self.Word4.path
            source_pdf = self.PDF4.path
        destination1 = Path(DOSSIER_PRIVE + 'relances/Relance{}-{}.docx'.format(k, facture.Numero_Facture))
        shutil.copy(source, destination1)
        destination2 = Path(
            DOSSIER_PRIVE + 'facturation_par_dossier/{}/Relance{}-{}.docx'.format(facture.Num_Affaire(), k,
                                                                                 facture.Numero_Facture))
        shutil.copy(source, destination2)
        destination_pdf1 = Path(DOSSIER_PRIVE + 'relances/Relance{}-{}.pdf'.format(k, facture.Numero_Facture))
        shutil.copy(source_pdf, destination_pdf1)
        destination_pdf2 = Path(
            DOSSIER_PRIVE + 'facturation_par_dossier/{}/Relance{}-{}.pdf'.format(facture.Num_Affaire(), k,
                                                                                  facture.Numero_Facture))
        shutil.copy(source_pdf, destination_pdf2)

    def effacer_pdf(self,k):
        facture = Facture.objects.get(id=self.ID_Facture_id)
        affaire = Affaire.objects.get(pk=facture.ID_Affaire_id)
        mission = Offre_Mission.objects.get(pk=affaire.ID_Mission_id)
        ingeprev = Ingeprev.objects.get(Nom='INGEPREV')
        payeur = Client.objects.get(pk=facture.ID_Payeur_id)
        envoi = Envoi_Facture.objects.get(pk=facture.ID_Envoi_Facture_id)

        d = Path(DOSSIER_PRIVE + 'relances/Relance{}-{}.docx'.format(k, facture.Numero_Facture))
        if os.path.isfile(d):
            os.remove(d)
        d = Path(DOSSIER_PRIVE + 'facturation_par_dossier/{}/Relance{}-{}.docx'.format(facture.Num_Affaire(), k,
                                                                                  facture.Numero_Facture))
        if os.path.isfile(d):
            os.remove(d)
        d = Path(DOSSIER_PRIVE + 'relances/Relance{}-{}.pdf'.format(k, facture.Numero_Facture))
        if os.path.isfile(d):
            os.remove(d)
            if k == 2:
                cree = facture.Fichier_Relance2_cree
            elif k == 3:
                cree = facture.Fichier_Relance3_cree
            elif k == 4:
                cree = facture.Fichier_Relance4_cree
            if cree:
                creer_pdf_relance2(k, facture, affaire, mission, ingeprev, DOSSIER_PRIVE, envoi, payeur)

        d = Path(DOSSIER_PRIVE + 'facturation_par_dossier/{}/Relance{}-{}.pdf'.format(facture.Num_Affaire(), k,
                                                                                  facture.Numero_Facture))
        if os.path.isfile(d):
            os.remove(d)
            if k == 2:
                cree = facture.Fichier_Relance2_cree
            elif k == 3:
                cree = facture.Fichier_Relance3_cree
            elif k == 4:
                cree = facture.Fichier_Relance4_cree
            if cree:
                source = Path(DOSSIER_PRIVE + 'relances/Relance{}-{}.pdf'.format(k, facture.Numero_Facture))
                destination = Path(
                    DOSSIER_PRIVE + 'facturation_par_dossier/{}/Relance{}-{}.pdf'.format(facture.Num_Affaire(), k,
                                                                                         facture.Numero_Facture))
                shutil.copy(source, destination)

    def copie_fichier(self):
        if self.Word2 != '' or self.Word3 != '' or self.Word4 != '':
            #pythoncom.CoInitialize()
            pass
        if self.Word2 != '':
            self.creer_pdf(2)
        if self.Word3 != '':
            self.creer_pdf(3)
        if self.Word4 != '':
            self.creer_pdf(4)

    def effacer_fichier(self):
        if (self.Word2 == '' and self.Word2_cree) or (self.PDF2 == '' and self.Word2_cree):
            self.effacer_pdf(2)
        if (self.Word3 == '' and self.Word3_cree) or (self.PDF3 == '' and self.Word3_cree):
            self.effacer_pdf(3)
        if (self.Word4 == '' and self.Word4_cree) or (self.PDF4 == '' and self.Word4_cree):
            self.effacer_pdf(4)

    def save(self, *args, **kwargs):
        self.effacer_fichier()
        if self.PDF2 == '':
            self.Word2 = ''
        if self.PDF3 == '':
            self.Word3 = ''
        if self.PDF4 == '':
            self.Word4 = ''
        if self.Word2 != '':
            self.Word2_cree = True
            self.Date_Creation_Word2 = timezone.now()
        else:
            self.Word2_cree = False
            self.Date_Creation_Word2 = None
            self.PDF2.delete()
        if self.Word3 != '':
            self.Word3_cree = True
            self.Date_Creation_Word3 = timezone.now()
        else:
            self.Word3_cree = False
            self.Date_Creation_Word3 = None
            self.PDF3.delete()
        if self.Word4 != '':
            self.Word4_cree = True
            self.Date_Creation_Word4 = timezone.now()
        else:
            self.Word4_cree = False
            self.Date_Creation_Word4 = None
            self.PDF4.delete()
        '''
        if self.id is None:
            saved_document = self.Word2
            self.Word2 = None
            super(Fichier_Word, self).save(*args, **kwargs)
            self.Word2 = saved_document
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
            '''

        super(Fichier_Word,self).save(*args, **kwargs)
        self.copie_fichier()

    def delete(self,*args,**kwargs):
        obj = Fichier_Word.objects.get(pk = self.pk)
        obj.Word2.delete()
        if os.path.isfile(self.Word2.path):
            os.remove(self.Word2.path)
            if os.path.isfile(self.PDF2.path):
                os.remove(self.PDF2.path)
        obj.Word3.delete()
        if os.path.isfile(self.Word3.path):
            os.remove(self.Word3.path)
            if os.path.isfile(self.PDF3.path):
                os.remove(self.PDF3.path)
        obj.Word4.delete()
        if os.path.isfile(self.Word4.path):
            os.remove(self.Word4.path)
            if os.path.isfile(self.PDF4.path):
                os.remove(self.PDF4.path)
        obj.PDF2.delete()
        if os.path.isfile(self.PDF2.path):
            os.remove(self.PDF2.path)
            if os.path.isfile(self.Word2.path):
                os.remove(self.Word2.path)
        obj.PDF3.delete()
        if os.path.isfile(self.PDF3.path):
            os.remove(self.PDF3.path)
            if os.path.isfile(self.Word3.path):
                os.remove(self.Word3.path)
        obj.PDF4.delete()
        if os.path.isfile(self.PDF4.path):
            os.remove(self.PDF4.path)
            if os.path.isfile(self.Word4.path):
                os.remove(self.Word4.path)
        super(Fichier_Word, self).delete(*args,**kwargs)

class InfoEmail(models.Model):
    From = models.EmailField(max_length=70, verbose_name = 'De')
    To = models.EmailField(max_length=70, verbose_name = 'A')
    Copie1 = models.EmailField(max_length=70, verbose_name = 'Copie à',null=True,blank=True)
    Copie2 = models.EmailField(max_length=70, verbose_name='Copie à',null=True,blank=True)
    Copie3 = models.EmailField(max_length=70, verbose_name='Copie à',null=True,blank=True)
    Subject = models.CharField(max_length = 100, verbose_name = 'Sujet', default = 'Facture Ingeprev')
    Message = models.TextField()
    File = models.FileField(blank = True)
    ID_Facture = models.IntegerField(null = True, blank = True)
    Type_Action = models.CharField(max_length = 100, blank = True)
    RAR = models.CharField(max_length = 20, blank = True, null = True)
    Suivi = models.CharField(max_length = 20, blank = True, null = True)

    def envoi_email(self):
        Subject = self.Subject
        From = self.From
        Message = self.Message
        To = self.To
        try:
            # send_mail(Subject, Message, From, ['admin@example.com'])
            email = EmailMessage(Subject, Message, From, [To])
            email.send()
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return redirect('sucess')

    def get_absolute_url(self):
        return reverse('admin: bdd_InfoEmail_change', kwargs={'pk': self.pk})

class Attachment(models.Model):
    message = models.ForeignKey(InfoEmail, verbose_name=_('InfoEmail'), on_delete=models.CASCADE)
    nom = models.CharField(max_length =70, blank = True)
    file = models.FileField(_('Attachment'), upload_to='tmp')

    def Num_Facture(self):
        mail = InfoEmail.objects.get(pk=self.message_id)
        idfacture = mail.ID_Facture
        facture = Facture.objects.get(pk=idfacture)
        numfacture = facture.Numero_Facture
        return numfacture

    def Nom_Fichier_Joint(self):
        mail = InfoEmail.objects.get(pk=self.message_id)
        idfacture = mail.ID_Facture
        facture = Facture.objects.get(pk=idfacture)
        numfacture = facture.Numero_Facture
        if self.nom !='Facture':
            return self.nom+'-'+str(numfacture)
        else:
            return str(numfacture)

    Nom_Fichier_Joint.short_description = 'Nom du Fichier'

    '''
    def Nom_Afficher(self):
        mail = InfoEmail.objects.get(pk=self.message_id)
        idfacture = mail.ID_Facture
        facture = Facture.objects.get(pk=idfacture)
        numfacture = facture.Numero_Facture
        if self.nom !=Facture:
            return self.nom+str(numfacture)
        else:
            return str(numfacture)
    '''

    def Chemin_Fichier(self):
        chemin = Path(DOSSIER + self.file.name)
        return chemin

    def selflink(self):
        if self.id:
            return "<a href='/link/to/volume/%s' target='_blank'>Edit</a>" % str(self.id)
        else:
            return "Not present"

    '''Ancien file_link'''
    def file_link(self):
        fichier = self.file
        return format_html(
            '<a{} target = "_blank">{}</a>', flatatt({'href': fichier.url}), fichier.name)

    def pdf(self):
        if self.id == None:
            return None
        else:
            return mark_safe(
                "<a href='{}' target='_blank'>PDF</a>".format(reverse('attachment_pdf', args=[self.id])))
            #nom_fichier = self.Nom_Fichier_Joint()
            #return mark_safe("<a href='{}' target='_blank'>{}</a>".format(reverse('attachment_pdf', args=[self.id]),nom_fichier))


    pdf.allow_tags = True
    pdf.short_description = 'Lien pdf'

    file_link.allow_tags = True
    file_link.short_description = 'Lien de Téléchargement'

    def delete(self,*args,**kwargs):
        obj = Attachment.objects.get(pk = self.pk)
        obj.file.delete()
        if os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super(Attachment, self).delete(*args,**kwargs)