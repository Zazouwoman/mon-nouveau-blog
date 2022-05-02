
from django.db import models
from django.db.models import Sum
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

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from .fonctions import *

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

class Ingeprev(models.Model):
    Nom = models.CharField(max_length=50, blank=True, verbose_name = 'Nom de la societe')
    logo = models.ImageField(upload_to='images',null=True,blank=True)
    SIRET = models.CharField(max_length=50, blank=True, verbose_name="N° de SIRET")
    Adresse = models.CharField(max_length=500, blank=True)
    Complement_Adresse = models.CharField(max_length=500, blank=True, verbose_name = "Complément d'Adresse")
    CP = models.CharField(validators=[CP_regex], max_length=5, verbose_name='Code postal', blank=True)
    Ville = models.CharField(max_length=150, blank=True)
    Type_Societe = models.CharField(max_length=150, blank=True, verbose_name = 'Statut juridique')
    Code_Banque = models.IntegerField(blank=True, null = True, verbose_name = 'Code Banque')
    Code_Guichet = models.IntegerField(blank=True, null = True, verbose_name='Code Guichet')
    Code_BIC = models.CharField(max_length=20, blank=True, verbose_name='Code BIC')
    Num_Compte = models.IntegerField(null=True, blank = True, verbose_name='Numéro de Compte')
    Cle = models.CharField(max_length=10, blank=True, verbose_name = 'Clé')
    Nom_Banque = models.CharField(max_length=100, blank=True, verbose_name = 'Nom de la Banque')
    Tel_Banque = models.CharField(validators=[tel_regex], max_length=16, verbose_name='Numéro de Téléphone de la banque',
                                        blank=True)
    IBAN = models.CharField(max_length=50, blank=True, verbose_name = 'IBAN')
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
    '''
    def selflink(self):
        if self.id:
            return "<a href='/link/to/volume/%s' target='_blank'>Edit</a>" % str(self.id)
        else:
            return "Not present"

    def file_link(self):
        fichier = self.file
        return format_html(
            '<a{} target = "_blank">{}</a>', flatatt({'href': fichier.url}), fichier.name)

    file_link.allow_tags = True
    file_link.short_description = 'Lien de Téléchargement'

    def delete(self,*args,**kwargs):
        obj = Ingeprev.objects.get(pk = self.pk)
        obj.file.delete()
        if os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super(Ingeprev, self).delete(*args,**kwargs)
    '''
    '''
    def save(self,*args,**args):
        obj = Ingeprev.objects.get(pk=self.pk)
    '''


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
    Denomination_Sociale = models.CharField(max_length = 50, verbose_name = "Dénomination sociale")
    SIRET = models.CharField(max_length = 50,blank=True, verbose_name = "N° de SIRET")
    Adresse = models.CharField(max_length = 500,blank=True)
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
    Denomination_Sociale = models.CharField(max_length=50, verbose_name = "Dénomination sociale")
    Adresse = models.CharField(max_length=500)
    CP = models.CharField(validators=[CP_regex], max_length=5, verbose_name='Code postal')
    Ville = models.CharField(max_length=150)
    Civilite = models.CharField(blank=True, choices=CiviliteType.choices, max_length=3)
    Nom_Contact = models.CharField(max_length=50, blank=True, verbose_name = "Nom")
    Prenom_Contact = models.CharField(max_length=50, blank=True, verbose_name = "Prénom")
    Tel_Contact = models.CharField(validators=[tel_regex], max_length=16, verbose_name='Numéro de téléphone',
                                        blank=True)
    Email_Contact = models.EmailField(max_length=70, blank=True, verbose_name = 'Email')
    Mode_Paiement = models.CharField(default = "Non défini", choices = ModePaiementType, max_length = 20, verbose_name = "Mode de Paiement")
    Delais_Paiement = models.IntegerField(default = 30, verbose_name = "Délais de Paiement (en jours)")
    Fin_Mois = models.CharField(choices = OuiOuNonType.choices , max_length = 3, default = "Non", verbose_name = "Fin de Mois")
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

    def Client(self):
        ID = self.ID_Envoi_Offre_id
        envoi_offre = Envoi_Offre.objects.get(id=ID)
        client = envoi_offre.Denomination_Sociale
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
    soldee = models.BooleanField(default = 'False')  #Pour savoir si l'affaire est soldée
    Type_Dossier = models.CharField(default = "A",max_length = 3)
    Indice_Dossier = models.IntegerField(default = 0,blank=True)
    Ref_Affaire = models.CharField(default = "A0001",max_length = 50, verbose_name = "Réf. Affaire")
    Nom_Affaire = models.CharField(max_length = 100, verbose_name = "Nom de l'Affaire", blank = True, null = True)
    ID_Mission = models.OneToOneField(Offre_Mission , on_delete=models.CASCADE, verbose_name = "Nom de la mission")
    ID_Client_Cache = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='%(class)s_ID_Client_Cache', blank=True,verbose_name="Client Caché", null=True)
    ID_Payeur = models.ForeignKey(Client,on_delete=models.SET_NULL, related_name='%(class)s_ID_Payeur', blank = True, verbose_name = "Payeur", null = True)
    ID_Envoi_Facture = models.ForeignKey(Envoi_Facture,on_delete=models.SET_NULL, blank = True, verbose_name = "Adresse Envoi Facture", null = True)
    Honoraires_Global = models.DecimalField(max_digits=12, decimal_places=2, verbose_name = 'Honoraire Global H.T.', default = 0)
    Date_Creation = models.DateField(default=date.today, verbose_name = "Date de création")
    Date_Previsionnelle = models.DateField(blank = True, null = True, default = None, verbose_name = "Date prévisionnelle de facturation")
    Type_Affaire = models.CharField(choices = AffaireType, max_length = 12, verbose_name = "Type d'Affaire", blank = True)
    ID_Pilote = models.ForeignKey(Pilote, on_delete=models.SET_NULL, verbose_name = "Pilote", blank = True, null = True)
    Etat = models.CharField(choices = EtatAffaireType, max_length = 8, verbose_name = "Etat de l'Affaire", default = "EC", blank = True)

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

    def Adresse(self):
        mission = Offre_Mission.objects.get(pk=self.ID_Mission_id)
        print(mission, mission.Adresse)
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

    def save(self,*args,**kwargs):
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
            self.save()
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

    class Meta:
        verbose_name_plural = "2. Affaires"

class Facture(models.Model):
    deja_validee = models.BooleanField(default = False, verbose_name = 'Validée') #Pour savoir si la facture a déjà été validée
    deja_envoyee = models.BooleanField(default = False, verbose_name = 'Envoyée') #Pour savoir si la facture a déjà été envoyée par mail
    deja_payee = models.BooleanField(default = False, verbose_name = 'Payée')  #Pour savoir si la facture a été payée ou non

    Numero_Facture = models.CharField(default = "",max_length = 50, verbose_name = "Numéro de facture", blank = True)
    Indice_Facture = models.IntegerField(default = 0,blank=True)
    ID_Affaire  = models.ForeignKey(Affaire , on_delete=models.CASCADE, verbose_name = "Nom de l'affaire")
    Nom_Affaire = models.CharField(max_length = 100, verbose_name = "Nom de l'Affaire", blank = True, null = True)
    ID_Payeur = models.ForeignKey(Client,on_delete=models.SET_NULL, null = True,verbose_name = "Payeur")
    ID_Envoi_Facture = models.ForeignKey(Envoi_Facture, on_delete=models.CASCADE,
                                         verbose_name="Adresse d'envoi de la facture", null = True)
    ID_Pilote = models.ForeignKey(Pilote, on_delete=models.SET_NULL, null = True, verbose_name = "Pilote")

    Descriptif = models.TextField()
    Montant_Facture_HT = models.DecimalField(max_digits=12, decimal_places=2, verbose_name = 'Montant de la facture H.T.', default = 0)
    Taux_TVA = models.CharField(choices = TVA, max_length = 2, verbose_name = "Taux de T.V.A.", default = "20")

    Date_Facture = models.DateField(default=date.today, verbose_name = "Date de la facture")

    Facture_Avoir = models.CharField(choices = FactureType, max_length = 10, verbose_name = "Facture ou Avoir", default = "FA")

    Etat = models.CharField(choices = EtatFacture, max_length = 8, verbose_name = "Etat", default = "BR")
    Etat_Paiement = models.CharField(choices = EtatPaiement, max_length = 8, verbose_name = "Etat du paiement", default = "ATT",blank = True)
    Date_Envoi = models.DateField(default=date.today, verbose_name="Date d'envoi", blank=True)
    Date_Relance1 = models.DateField(default=date.today, verbose_name="Date de relance1 - relance par mail", blank=True)
    Date_Relance2 = models.DateField(default=date.today, verbose_name="Date de relance2 - relance téléphonique", blank=True)
    Date_Relance3 = models.DateField(default=date.today, verbose_name="Date de relance3 - relance courrier", blank=True)
    Date_Relance4 = models.DateField(default=date.today, verbose_name="Date de relance4 - relance RAR", blank=True)
    Date_Relance5 = models.DateField(default=date.today, verbose_name="Date de relance5 - mise en demeure", blank=True)
    Date_Relance6 = models.DateField(default=date.today, verbose_name="Date de relance6 - contentieux", blank=True)
    Date_Dernier_Rappel = models.DateField(default=date.today, verbose_name = "Date dernier rappel", blank = True)
    Num_Relance = models.IntegerField(default = 0, blank = True)
    Num_RAR = models.CharField(max_length = 20, blank = True, default = 'A préciser', verbose_name = "Numéro RAR relance 4") #Numéro du RAR de la relance 4
    Num_RAR_Demeure = models.CharField(max_length = 20, blank = True, default = 'A préciser', verbose_name = "Numéro RAR mise en demeure") #Numéro du RAR de la mise en demeure

    Mode_Paiement = models.CharField(default="Non défini", choices=ModePaiementType, max_length=20,
                                     verbose_name="Mode de Paiement")
    Delais_Paiement = models.IntegerField(default=30, verbose_name="Délais de Paiement (en jours)")
    Fin_Mois = models.CharField(choices=OuiOuNonType.choices, max_length=3, default="Non", verbose_name="Fin de Mois")
    Modalites_Paiement = models.TextField(blank=True, verbose_name="Modalités particulières de Paiement")

    Denomination_Client = models.CharField(max_length=50, verbose_name="Dénomination sociale Client")
    Adresse_Client = models.CharField(max_length=500, blank=True)
    CP_Client = models.CharField(validators=[CP_regex], max_length=5, verbose_name='Code postal', blank=True)
    Ville_Client = models.CharField(max_length=150, blank=True)
    Civilite_Client = models.CharField(blank=True, choices=CiviliteType.choices, max_length=3, verbose_name = "Civilité")
    Nom_Client = models.CharField(max_length=50, blank=True, verbose_name="Nom")
    Prenom_Client = models.CharField(max_length=50, blank=True, verbose_name="Prénom")
    Email_Client = models.EmailField(max_length=70, blank=True, verbose_name="Email")

    Denomination_Facture = models.CharField(max_length=50, verbose_name="Dénominsation sociale Facture")
    Adresse_Facture = models.CharField(max_length=500)
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

    class Meta:
        verbose_name_plural = "3. Factures"

    def Montant_Facture_TTC(self):
        return self.Montant_Facture_HT * (100+int(self.Taux_TVA))/100

    def save(self,*args,**kwargs):
        if self.Numero_Facture == '':  #Lors de la création de la facture = remplissage automatique des champs connus
            affaire = Affaire.objects.get(pk=self.ID_Affaire_id)
            self.ID_Payeur = affaire.ID_Payeur
            self.Nom_Affaire = affaire.Nom_Affaire
            self.ID_Envoi_Facture = affaire.ID_Envoi_Facture
            self.ID_Pilote = affaire.ID_Pilote
            self.Numero_Facture = 'FA0001'
            self.save()
        if not self.deja_validee:
            self.deja_payee = False
        if self.deja_payee:
            self.Etat_Paiement = 'PAYE'
        if not self.deja_payee:
            self.Etat_Paiement = 'ATT'
        super().save(*args,**kwargs)

    def Reste_Affaire(self):
        affaire = Affaire.objects.get(pk = self.ID_Affaire_id)
        reste = affaire.Reste_A_Regler()
        return '{:,.2f}'.format(reste).replace(',', ' ').replace('.', ',')

    def Honoraire_Affaire(self):
        affaire = Affaire.objects.get(pk=self.ID_Affaire_id)
        honoraire = affaire.Honoraires_Global
        return '{:,.2f}'.format(honoraire).replace(',', ' ').replace('.', ',')

    def Date_Prev_Affaire(self):
        affaire = Affaire.objects.get(pk=self.ID_Affaire_id)
        return affaire.Date_Previsionnelle

    def Num_Affaire(self):
        affaire = Affaire.objects.get(pk=self.ID_Affaire_id)
        return affaire.Ref_Affaire

    def Client_Cache(self):
        affaire = Affaire.objects.get(pk=self.ID_Affaire_id)
        return affaire.client()

    def Date_Echeance1(self):
        if self.Fin_Mois == "Non":
            echeance = self.Date_Facture + timedelta(days=self.Delais_Paiement)
        elif self.Fin_Mois == "Oui":
            echeance1 = self.Date_Facture + timedelta(days=self.Delais_Paiement)
            premier = date(echeance1.year, echeance1.month, 1)
            dernier = premier + relativedelta(months=1, days=-1)
            echeance = dernier
        return echeance

    def Date_Relance(self):
        dateecheance1 = self.Date_Echeance1()
        relance = self.Num_Relance
        daterelance = dateecheance1 + timedelta(days = 30*relance)
        return daterelance

    Reste_Affaire.short_description = "Montant de l'affaire qu'il reste à facturer"
    Honoraire_Affaire.short_description = "Montant honoraires de l'affaire"

    def Remplissage_Facture(self):
        self.save()
        payeur = Client.objects.get(pk=self.ID_Payeur_id)
        self.Denomination_Client = payeur.Denomination_Sociale
        self.Adresse_Client = payeur.Adresse
        self.CP_Client = payeur.CP
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
        self.CP_Facture = facture.CP
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
        self.CP_Client = payeur.CP
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
        self.CP_Facture = facture.CP
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


class InfoEmail(models.Model):
    From = models.EmailField(max_length=70, verbose_name = 'De')
    To = models.EmailField(max_length=70, verbose_name = 'A')
    Subject = models.CharField(max_length = 200, verbose_name = 'Sujet', default = 'Facture Ingeprev')
    Message = models.TextField()
    File = models.FileField(blank = True)
    #ID_Facture = models.ForeignKey(Facture, related_name = '%(class)s_ID_Facture', on_delete = models.SET_NULL, blank = True, null = True)
    ID_Facture = models.IntegerField(null = True, blank = True)
    Type_Action = models.CharField(max_length = 100, blank = True)
    RAR = models.CharField(max_length = 100, blank = True, null = True)

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
    file = models.FileField(_('Attachment'), upload_to='attachments')

    def selflink(self):
        if self.id:
            return "<a href='/link/to/volume/%s' target='_blank'>Edit</a>" % str(self.id)
        else:
            return "Not present"

    def file_link(self):
        fichier = self.file
        return format_html(
            '<a{} target = "_blank">{}</a>', flatatt({'href': fichier.url}), fichier.name)

    file_link.allow_tags = True
    file_link.short_description = 'Lien de Téléchargement'

    def delete(self,*args,**kwargs):
        obj = Attachment.objects.get(pk = self.pk)
        obj.file.delete()
        if os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super(Attachment, self).delete(*args,**kwargs)


