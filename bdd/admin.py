# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from pathlib import Path
from django.core.files import File
from django.http import FileResponse

from django.template.loader import get_template
from dateutil.relativedelta import relativedelta

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages, admin
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.utils import label_for_field
from django.db.models import Sum
from django.core.exceptions import FieldDoesNotExist
from django.utils.html import strip_tags
from django.forms.widgets import TextInput
from datetime import date

from pathlib import Path
import shutil


from xhtml2pdf import pisa

import tempfile

from .fonctions import *
from .models import *
from .forms import *
from decimal import Decimal
# Register your models here.

#DOSSIER = 'media/'
# en mettant media ils sont enregistrés dans F:\media, en mettant '/media/' ils sont enregistrés
# sur le serveur....
DOSSIER = settings.MEDIA_ROOT #Nom du dossier dans lequel sont enregistrés les factures, lettres de relance

admin.site.site_header = "UMSRA Admin"

#Définition des permissions pour l'affichage ou non dans le menu admin - Choisir entre personne ne voit ou bien seulement les superuse voient
class IngeprevAdmin(admin.ModelAdmin):
    list_display = ['Nom','Capital',]
    formfield_overrides = {models.DecimalField: {
        'widget': forms.TextInput(attrs={'style': 'text-align:right;', }),
    },
    }
    localized_fields = ('Capital',)


class EnvoiOffreAdmin(admin.ModelAdmin):
    def get_model_perms(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request, *args, **kwargs)

class EnvoiFactureAdmin(admin.ModelAdmin):
    form = EnvoiFactureForm

    def get_model_perms(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request)

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file']

class AttachmentAdmin(admin.ModelAdmin):
    def get_model_perms(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request)

class CompteurIndiceAdmin(admin.ModelAdmin):
    def get_model_perms(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request)

#class AttachmentInline(admin.StackedInline):
class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    fields = ['nom','file']
    '''Version fichiers liés non modifiables (mise dans AttachmentInline2: 
    on peut rajouter un seul fichier joint, on peut supprimer un ou plusieurs des fichiers préjoints
    Intérêt : quand on clique sur les fichiers qui sont déjà présents ils s'ouvrent dans une nouvelle fenêtre, sinon c'est dans la même fenêtre.
    fields = ['nom','file_link',]
    readonly_fields = ['nom','file_link',]
    '''

    def get_model_perms(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request)

    def __init__(self,*args,**kwargs):
        super(AttachmentInline,self).__init__(*args,**kwargs)

class AttachmentInline2(admin.TabularInline):
    model = Attachment
    extra = 0
    #fields = ['nom','file']
    '''Version fichiers liés non modifiables : 
    on peut rajouter un seul fichier joint, on peut supprimer un ou plusieurs des fichiers préjoints
    Intérêt : quand on clique sur les fichiers qui sont déjà présents ils s'ouvrent dans une nouvelle fenêtre, sinon c'est dans la même fenêtre.
    '''
    fields = ['nom','file_link',]
    readonly_fields = ['nom','file_link',]

    def get_model_perms(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request)

    def __init__(self,*args,**kwargs):
        super(AttachmentInline2,self).__init__(*args,**kwargs)

class InfoEmailAdmin(admin.ModelAdmin):
    list_display = ('Subject',)
    form = InfoEmailForm
    change_form_template = 'bdd/Creation_Email.html'
    inlines = [AttachmentInline,]  #Cas où il y a effectivement un email
    other_set_inlines = [AttachmentInline2,]  #Cas des relances où il n'y a pas de mail

    def get_model_perms(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request)

    def get_inlines(self, request, obj=None):
        if obj and obj.Type_Action in ['Relance2','Relance3','Relance4','Relance5','Relance6']:
            return self.other_set_inlines
        else:
            return self.inlines

    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            form = InfoEmailForm
        elif obj.Type_Action == 'Relance2':
            form = RelanceForm2
        elif obj.Type_Action == 'Relance3':
            form = RelanceForm3
        elif obj.Type_Action == 'Relance4':
            form = RelanceForm4
        elif obj.Type_Action == 'Relance5':
            form = RelanceForm5
        elif obj.Type_Action == 'Relance6':
            form = RelanceForm6
        else:
            form = super().get_form(request, obj, **kwargs)
        return form

    def change_view(self,request, object_id, extra_context = None):
        email = InfoEmail.objects.get(pk = object_id)
        factureid = email.ID_Facture
        facture = Facture.objects.get(pk=factureid)
        #facture_form = FactureForm(instance = facture)
        visualisation_facture_form = VisualisationFactureForm(instance = facture)
        envoifacture = Envoi_Facture.objects.get(pk = facture.ID_Envoi_Facture_id)
        historique_form = FactureHistoriqueForm(instance = facture)
        extra_context = extra_context or {}

        suivi = facture.Num_Suivi
        if suivi == 'A préciser' or suivi == ' ':
            extra_context['Suivi'] = False
        else:
            extra_context['Suivi'] = True
        print(suivi, extra_context['Suivi'])

        if facture.Num_Relance != 4:
            RAR = facture.Num_RAR
        else:
            RAR = facture.Num_RAR_Demeure
        if RAR == 'A préciser' or RAR == ' ':
            extra_context['RAR'] = False
        else:
            extra_context['RAR'] = True

        envoi_facture_form = EnvoiFactureForm(instance = envoifacture)
        #extra_context['facture_form'] = facture_form
        extra_context['facture_form'] = visualisation_facture_form
        extra_context['relance'] = facture.Num_Relance
        extra_context['envoi_facture_form'] = envoi_facture_form
        extra_context['subject'] = email.Subject
        extra_context['facture'] = facture
        extra_context['envoifacture'] = envoifacture
        extra_context['historique_form'] = historique_form

        if facture.Facture_Avoir == 'FA':
            extra_context['FA'] = True
        else:
            extra_context['FA'] = False

        if "Relancer" in request.POST:
            num = facture.Num_Relance
            mise_a_jour_relance(facture, num)
            email.delete()
            messages.add_message(request, messages.INFO, 'Relance {} enregistrée avec succès !!'.format(num))
            if 2 <= num <= 4:
                source = Path(DOSSIER + 'relances/Relance{}-{}.pdf'.format(num,facture.Numero_Facture))
                destination = Path(DOSSIER + 'facturation_par_dossier/{}/Relance{}-{}.pdf'.format(facture.Num_Affaire(),num,facture.Numero_Facture))
                shutil.copy(source, destination)
            url = '/admin/bdd/facture/'
            return redirect(url)

        if "Fermer" in request.POST:
            if facture.Num_Relance < 4:
                facture.Num_RAR = 'A préciser'
            elif facture.Num_Relance == 4:
                facture.Num_RAR_Demeure = 'A préciser'
            if facture.Num_Relance == 2:
                facture.Num_Suivi = 'A préciser'
            facture.save()
            if facture.Num_Relance == 0 and facture.Facture_Avoir == "FA":
                messages.add_message(request, messages.WARNING, "Votre facture n'a pas été envoyée.")
            elif facture.Num_Relance == 0 and facture.Facture_Avoir == "AV":
                messages.add_message(request, messages.WARNING, "Votre avoir n'a pas été envoyé. Si vous souhaitez valider son paiement sans l'envoyer il faut le faire manuellement.")
            else:
                messages.add_message(request, messages.WARNING, "Votre dernière opération n'a pas été validée. La relance n'a donc pas été enregistrée.")
            email.delete()
            url = '/admin/bdd/facture'
            return redirect(url)
        return super().change_view(request, object_id, extra_context = extra_context)

    def response_change(self, request, obj):
        email = obj
        factureid = email.ID_Facture
        facture = Facture.objects.get(pk=factureid)
        num = facture.Num_Relance

        if "Fermer" in request.POST:
            if num < 4:
                facture.Num_RAR = 'A préciser'
            elif num == 4:
                facture.Num_RAR_Demeure = 'A préciser'
            if num == 2:
                facture.Num_Suivi = 'A préciser'
            facture.save()
            if num == 0 and facture.Facture_Avoir == "FA":
                messages.add_message(request, messages.WARNING, "Votre facture n'a pas été envoyée.")
            elif num and facture.Facture_Avoir == "AV":
                messages.add_message(request, messages.WARNING, "Votre avoir n'a pas été envoyé. Si vous souhaitez valider son paiement sans l'envoyer il faut le faire manuellement.")
            else:
                messages.add_message(request, messages.WARNING, "Aucune relance n'a été effectuée. Opération annulée.")
            email.delete()
            url = '/admin/bdd/facture'
            return redirect(url)

        if "Relancer" in request.POST:
            mise_a_jour_relance(facture, num)
            email.delete()
            messages.add_message(request, messages.INFO, 'Relance {} sur la facture n°{} enregistrée avec succès !!'.format(num,facture.Numero_Facture))
            if 2 <= num <= 4:
                source = Path(DOSSIER + 'relances/Relance{}-{}.pdf'.format(num, facture.Numero_Facture))
                destination = Path(
                    DOSSIER + 'facturation_par_dossier/{}/Relance{}-{}.pdf'.format(facture.Num_Affaire(), num,
                                                                                   facture.Numero_Facture))
                shutil.copy(source, destination)
            url = '/admin/bdd/facture/'
            return redirect(url)

        if ("Valider_Suivi" in request.POST) or ("Mettre_a_jour_Suivi" in request.POST):
            if obj.Suivi == 'A préciser':
                messages.add_message(request, messages.ERROR,
                                     "Vous devez rentrer un numéro de Suivi valide. Il ne s'est rien passé !!")
                return redirect('.')
            else:
                messages.add_message(request, messages.WARNING,
                                     'Le numéro de Suivi a été mis à jour. Vous pouvez maintenant cliquer sur le bouton "Relance Faite" pour valider la relance.')
                facture.Num_Suivi = obj.Suivi
                facture.save()
                return redirect('.')

        if ("Valider_RAR" in request.POST) or ("Mettre_a_jour_RAR" in request.POST):
            if obj.RAR == 'A préciser':
                messages.add_message(request, messages.ERROR, "Vous devez rentrer un numéro de RAR valide. Il ne s'est rien passé !!")
                return redirect('.')
            else:
                messages.add_message(request, messages.WARNING,
                                     """Le numéro de RAR a été mis à jour. La dernière lettre relance est maintenant à jour. Vous pouvez maintenant imprimer le tout et cliquer sur le bouton "Relance Faite" pour valider la relance quand c'est envoyé.""")

            if num == 3:
                facture.Num_RAR = obj.RAR
            elif num == 4:
                facture.Num_RAR_Demeure = obj.RAR
            facture.save()

            affaire = Affaire.objects.get(pk=facture.ID_Affaire_id)
            mission = Offre_Mission.objects.get(pk=affaire.ID_Mission_id)
            ingeprev = Ingeprev.objects.get(Nom='INGEPREV')

            # Création du pdf dans media
            data = {}
            data['facture'] = facture
            data['Ref_Affaire'] = affaire.Ref_Affaire
            data['affaire'] = affaire
            data['Date_Echeance'] = facture.Date_Echeance1()
            data['Montant_TTC'] = facture.Montant_Facture_TTC()
            data['ingeprev'] = ingeprev
            data['mission'] = mission
            data['date'] = date.today()
            data['nb'] = facture.Nb_Avoir()
            data['avoir'] = facture.Avoirs_Lies()
            data['montant_avoir_lie'] = facture.Montants_Avoirs_Lies_TTC()
            data['solde'] = facture.Solde_Pour_Avoir_Eventuel()
            if adresses_identiques(facture):
                data['identiques'] = True
            else:
                data['identiques'] = False
            if facture.Facture_Avoir == 'FA':
                data['FA'] = True
            else:
                data['FA'] = False

            if num == 3:
                if "Mettre_a_jour_RAR" in request.POST:
                    attachment = Attachment.objects.filter(message_id = email.id).filter(nom = "Lettre de Relance 3")
                    attachment.delete()
                source_html = 'bdd/Lettre_Relance3.html'
                fichier = DOSSIER + 'relances/Relance3-{}.pdf'.format(facture.Numero_Facture)
                creer_html_to_pdf(source_html, fichier, data)
                chemin = Path(fichier)
                with chemin.open(mode='rb') as f:
                     Attachment.objects.create(file=File(f, name=chemin.name), message=email, nom = "Lettre de Relance 3")

            if num == 4:
                if "Mettre_a_jour_RAR" in request.POST:
                    attachment = Attachment.objects.filter(message_id = email.id).filter(nom = "Lettre de Relance 4")
                    attachment.delete()
                source_html = 'bdd/Lettre_Relance4.html'
                fichier = DOSSIER + 'relances/Relance4-{}.pdf'.format(facture.Numero_Facture)
                creer_html_to_pdf(source_html, fichier, data)
                chemin = Path(fichier)
                with chemin.open(mode='rb') as f:
                     Attachment.objects.create(file=File(f, name=chemin.name), message=email, nom = "Lettre de Relance 4")
            return redirect('.')

        if "Envoyer" in request.POST:
            obj.save()
            Subject = obj.Subject
            From = obj.From
            Message = obj.Message
            To = obj.To
            try:
                attachments = []  # start with an empty list
                attach_files = Attachment.objects.filter(message_id = obj.pk)

                email = EmailMessage(Subject, Message, From, [To], ['compta@ingeprev.com'], attachments = attachments)

                for attach in attach_files:
                    f = settings.MEDIA_ROOT + attach.file.name
                    #f = settings.MEDIA_URL + attach.file.name
                    if isinstance(f, str):
                        email.attach_file(f)
                    elif isinstance(f, (tuple, list)):
                        n, fi, mime = f + (None,) * (3 - len(f))
                        email.attach(n, fi, mime)

                #email.content_subtype = "html"
                email.send()

            except BadHeaderError:
                return HttpResponse("Erreur, l'email n'a pas été envoyé.")

            facture = Facture.objects.get(pk = obj.ID_Facture)
            num = facture.Num_Relance
            mise_a_jour_relance(facture, num)
            facture.save()
            obj.delete()
            messages.add_message(request, messages.INFO, 'Votre email a été envoyé avec succès !!')
            url = '/admin/bdd/facture/'
            return redirect(url)

        return super().response_change(request, obj)

class ClientAdmin(admin.ModelAdmin):
    list_display = ("Denomination_Sociale", "SIRET", "Adresse", "CP", "Ville", 'Total_Affaire')
    search_fields = ("Denomination_Sociale__startswith",)
    form = ClientForm
    list_per_page = 12

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

class Offre_MissionAdminForm(forms.ModelForm):
    class Meta:
        model = Offre_Mission
        #fields = ['Ref_Mission','Nom_Mission','Adresse','CP','ID_Payeur','ID_Envoi_Offre','ID_Client_Cache','ID_Apporteur',
                  #'Honoraires_Proposes','Date_Proposition','Descriptif','ID_Pilote']
        exclude = ['Type_Dossier','Indice_Dossier','Etat','Date_Acceptation']
    def __init__(self, *args, **kwargs):
        super(Offre_MissionAdminForm, self).__init__(*args, **kwargs)
        self.fields['Ref_Mission'].widget.attrs['readonly'] = True

class Offre_MissionAdmin(admin.ModelAdmin):
    list_display = ("Nom_Mission", "ID_Payeur", "Client", "Adresse", "CP", "Ville","ID_Pilote",'Date_Proposition','Etat')
    search_fields = ("Nom_Mission__startswith",)
    list_filter = ('Etat','ID_Pilote',)
    form = Offre_MissionForm
    change_form_template = 'bdd/Offre_Mission.html'
    formfield_overrides = {models.DecimalField: {
            'widget': forms.TextInput(attrs={'style': 'text-align:right;', }),
        },
    }
    list_per_page = 12

    class  Meta:
        model = Offre_Mission

    def delete_model(self, request, obj):
        obj.custom_delete()
        if obj.Etat == 'ACC':
            messages.warning(request, "L'offre est déjà acceptée. Elle ne peut pas être supprimée.")
            #messages.success(request, "")
            #messages.add_message(request, messages.WARNING, "L'offre est déjà acceptée. Elle ne peut pas être supprimée.")

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.custom_delete()
        messages.add_message(request, messages.WARNING, "Seules les offres non acceptées ont été supprimées.")

    def get_form(self, request, obj=None, **kwargs):

        if not obj:
            form = Offre_MissionAdminForm
        else:
            form = Offre_MissionForm

        return super().get_form(request,**kwargs)

    def get_readonly_fields(self, request, obj = None):
        return ['Etat','Date_Acceptation']

    def change_view(self,request, object_id, extra_context = None):
        extra_context = extra_context or {}
        obj = Offre_Mission.objects.get(pk=object_id)
        if obj.Etat == 'ATT':
            extra_context['attente'] = True
        else:
            extra_context['attente'] = False
        if obj.Etat =='ACC':
            extra_context['accepte'] = True
        else:
            extra_context['accepte'] = False
        print('ici1')
        return super().change_view(request, object_id, extra_context=extra_context)

    def response_change(self, request, obj):
        if "Sans_Suite" in request.POST:
            if obj.Etat == "ATT":
                obj.Etat = "REF"
                obj.save()
                return redirect('.')
            elif obj.Etat == "ACC":
                messages.add_message(request, messages.ERROR,
                                     "Impossible de classer cette offre de mission sans suite. Elle a déjà été acceptée.")
                return redirect('.')
        if "Valider_Offre" in request.POST:
            if obj.Etat =="ACC":
                messages.add_message(request, messages.ERROR,
                                     "Impossible de créer l'affaire. Cette offre de mission est déjà acceptée.")
                return redirect('.')
            elif obj.Etat == 'REF':
                messages.add_message(request, messages.ERROR,
                                     "Impossible de créer l'affaire. Cette offre de mission est refusée.")
                return redirect('.')
            else:
                obj.save()
                idmission = obj.pk
                aujourdhui = date.today()
                annee = aujourdhui.year
                mois = aujourdhui.month
                periode = '{}{:02d}'.format(annee, mois)
                indice = calcul_indice('A', periode)
                refaffaire = 'A-{}{:04d}'.format(periode, indice)
                obj.Etat = "ACC"
                obj.Date_Acceptation = aujourdhui
                obj.save()
                idpayeur = obj.ID_Payeur
                idclientcache = obj.ID_Client_Cache
                nomaffaire = obj.Nom_Mission
                honorairesglobal = obj.Honoraires_Proposes
                idpilote = obj.ID_Pilote
                affaire = Affaire.objects.create(ID_Mission_id=idmission, Ref_Affaire=refaffaire, Indice_Dossier = indice,
                                                 ID_Payeur=idpayeur, ID_Client_Cache=idclientcache,
                                                 Nom_Affaire=nomaffaire,Honoraires_Global=honorairesglobal,
                                                 ID_Pilote=idpilote)
                messages.warning(request,
                                 "L'adesse d'envoi de la facture a été créée à l'identique de l'adresse du payeur avec les modalités de paiement par défaut. Vous pouvez la modifier si besoin.")
                id = affaire.pk
                url = '/admin/bdd/affaire/{}/change'.format(id)
                return redirect(url, pk=id)
        return super().response_change(request, obj)


#Filtre du prévisionnel de facturation
class Previsionnel_Filter(admin.SimpleListFilter):
    title = "Prévisionnel de facturation"
    parameter_name = 'Prev'

    def lookups(self, request, model_admin):
        return(('A_Rec','A recaler'),
               ('Mois','Mois en cours'),
               ('Annee', 'Année comptable en cours'),
               ('A_venir','Années à venir'),
               )

    def queryset(self, request, queryset):
        aujourdhui = date.today()
        if self.value() == 'A_Rec':
            q_array = []
            for element in queryset:
                if (not element.Date_Previsionnelle) or (element.Date_Previsionnelle and element.Date_Previsionnelle <= date.today()):
                    if float(element.Reste_A_Regler()) > 0.001:
                        q_array.append(element.id)
            return queryset.filter(pk__in=q_array)
        if self.value() == 'Mois':
            q_array = []
            premier = date(aujourdhui.year, aujourdhui.month, 1)
            finmois = premier + relativedelta(months=1, days=-1)
            for element in queryset:
                if element.Date_Previsionnelle and aujourdhui < element.Date_Previsionnelle <= finmois:
                    if float(element.Reste_A_Regler()) > 0.001:
                        q_array.append(element.id)
            return queryset.filter(pk__in=q_array)
        if self.value() == 'Annee':
            q_array = []
            finannee = date(aujourdhui.year,12,31)
            for element in queryset:
                if element.Date_Previsionnelle and element.Date_Previsionnelle <= finannee:
                    if float(element.Reste_A_Regler()) > 0.001:
                        q_array.append(element.id)
            return queryset.filter(pk__in=q_array)
        if self.value() == 'A_venir':
            q_array = []
            finannee = date(aujourdhui.year,12,31)
            for element in queryset:
                if (not element.Date_Previsionnelle) or (element.Date_Previsionnelle and element.Date_Previsionnelle > finannee):
                    if float(element.Reste_A_Regler()) > 0.001:
                        q_array.append(element.id)
            return queryset.filter(pk__in=q_array)

#Filtre des affaires à solder
class ASolder_Filter(admin.SimpleListFilter):
    title = "Affaire à solder"
    parameter_name = 'Solder'

    def lookups(self, request, model_admin):
        return(('A_Solder','A solder'),
               ('En_Cours','En cours'),
               )

    def queryset(self, request, queryset):
        if self.value() == 'A_Solder':
            q_array = []
            for element in queryset:
                if abs(float(element.Solde())) <= 10**-3:
                    if not element.soldee:
                        q_array.append(element.id)
            return queryset.filter(pk__in=q_array)
        if self.value() =='En_Cours':
            q_array = []
            for element in queryset:
                if not element.soldee:
                    q_array.append(element.id)
            return queryset.filter(pk__in= q_array)


#class AffaireAdmin(TotalsumAdmin):
class AffaireAdmin(admin.ModelAdmin):
    list_display = ("Nom_Affaire", "ID_Payeur", "Honoraires_Global", 'Reste_A_Regler', 'Solde', "Date_Previsionnelle", 'soldee',)
    search_fields = ("Nom_Affaire__startswith",)
    list_filter = (Previsionnel_Filter, ASolder_Filter, 'ID_Pilote', 'Etat')
    radio_fields = {"Type_Affaire":admin.HORIZONTAL,"Etat":admin.HORIZONTAL}
    list_editable = ('Date_Previsionnelle','soldee',)
    totalsum_list = ('Honoraires_Global','Reste_A_Regler','Solde',)
    localized_fields = ('Honoraires_Global','Reste_A_Regler',)
    list_per_page = 9
    formfield_overrides = {models.DecimalField: {
            'widget': forms.TextInput(attrs={'style': 'text-align:right;', }),
        },
    }

    unit_of_measure = ""
    totalsum_decimal_places = 2
    change_list_template = 'bdd/Liste_Affaires.html'
    form = AffaireForm
    change_form_template = 'bdd/Modification_Affaire.html'

    class Meta:
        model = Affaire

    def save_model(self, request,obj,form,change):
        if obj.ID_Envoi_Facture == None and obj.ID_Payeur != None:
            messages.warning(request,
                          "L'adesse d'envoi de la facture a été créée à l'identique de l'adresse du payeur avec les modalités de paiement par défaut. Vous pouvez la modifier si besoin.")
        obj.save()

    def delete_model(self, request, obj):
        obj.custom_delete()
        if obj.Etat == 'EC':
            messages.warning(request, "L'affaire est en cours. Elle ne peut pas être supprimée.")
            #messages.success(request, "")
            #messages.add_message(request, messages.WARNING, "L'offre est déjà acceptée. Elle ne peut pas être supprimée.")

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.custom_delete()
        messages.add_message(request, messages.WARNING, "Seules les affaires archivées ont été supprimées.")

    def get_readonly_fields(self, request, obj = None):
        if not obj:
            return []
        else:
            return ('Affiche_Reste_A_Regler','Adresse','CP','Ville',)

    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            return CreationAffaireForm
        return super().get_form(request, obj, **kwargs)

    def get_changelist_form(self, request, **kwargs):
        #self.readonly_fields = ('Solde', )
        return super().get_changelist_form(request, **kwargs)

    def response_add(self, request, obj, post_url_continue=None):
        id = obj.id
        url = '/admin/bdd/affaire/{}/change'.format(id)
        return redirect(url)

    def response_change(self, request, obj):
        if "Facturer" in request.POST:
            obj.save()
            idaffaire = obj.pk
            affaire = obj
            idpayeur = affaire.ID_Payeur
            nomaffaire = affaire.Nom_Affaire
            idenvoifacture = affaire.ID_Envoi_Facture
            idpilote = affaire.ID_Pilote
            numfacture = 'FA0001'
            refclient = affaire.Ref_Client
            facture = Facture.objects.create(ID_Affaire_id=idaffaire,
                                             ID_Payeur = idpayeur, Nom_Affaire = nomaffaire,
                                             ID_Envoi_Facture = idenvoifacture, ID_Pilote = idpilote,
                                             Numero_Facture = numfacture,Ref_Client = refclient)

            id = facture.pk
            url = '/admin/bdd/facture/{}/change'.format(id)
            return redirect(url, pk=id)
        return super().response_change(request, obj)

    def changelist_view(self, request, extra_context=None):
        response = super(AffaireAdmin, self).changelist_view(request, extra_context)
        if not hasattr(response, "context_data") or "cl" not in response.context_data:
            return response
        filtered_query_set = response.context_data["cl"].queryset
        extra_context = extra_context or {}
        extra_context["totals"] = {}
        extra_context["unit_of_measure"] = self.unit_of_measure

        for elem in self.totalsum_list:
            try:
                self.model._meta.get_field(elem)  # Checking if elem is a field
                total = filtered_query_set.aggregate(totalsum_field=Sum(elem))["totalsum_field"]
                if total is not None:
                    extra_context["totals"][
                        label_for_field(elem, self.model, self)] = round(total, self.totalsum_decimal_places)
            except FieldDoesNotExist:  # maybe it's a property
                if hasattr(self.model, elem):
                    total = 0
                    for f in filtered_query_set:
                        try:
                            total += getattr(f, elem, 0)
                        except TypeError:
                            # This allows calculating totals of columns
                            # that are generated from functions in the model
                            # by simply calling the function reference that 
                            # getattr returns 
                            total += getattr(f, elem, 0)()
                    extra_context["totals"][
                        label_for_field(elem, self.model, self)
                    ] = round(total, self.totalsum_decimal_places)

        response.context_data.update(extra_context)
        return response

#Filtre des factures à relancer
class A_Relancer_Filter(admin.SimpleListFilter):
    title = "Factures à relancer"
    parameter_name = 'Relance'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each tuple is the coded value for the option that will appear in the URL query. The second element is the
        human-readable name for the option that will appear in the right sidebar.
        """
        return(('Total','Toutes les relances'),
               ('Rel1','1ère relance (Email)'),
               ('Rel2','2ème relance (Courrier Suivi)'),
               ('Rel3','3ème relance (RAR)'),
               ('Rel4','4ème relance (Mise en Demeure)'),
               ('Rel5', 'A mettre en conciliation'),
               ('Rel6', 'A mettre en assignation'),
               ('Rel7', 'Assignation faite'),)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in the query string and retrievable via `self.value()`.
        """
        if self.value() == 'Total':
            q_array = []
            for element in queryset:
                if element.deja_envoyee == True and not element.deja_payee and element.Date_Relance() <= date.today():
                    q_array.append(element.id)
            return queryset.filter(pk__in=q_array)

        for k in range(1,8):
            titre = 'Rel{}'.format(k)
            if self.value() == titre:
                q_array = []
                for element in queryset:
                    if element.deja_envoyee == True and not element.deja_payee and element.Num_Relance == k and element.Date_Relance() <= date.today():
                        q_array.append(element.id)
                return queryset.filter(pk__in = q_array)

#Filtre des factures validées mais non envoyées
class A_Envoyer_Filter(admin.SimpleListFilter):
    title = "Factures validées à envoyer"
    parameter_name = 'Envoi'

    def lookups(self, request, model_admin):
        return(('A_Env','A envoyer'),
               )

    def queryset(self, request, queryset):
        if self.value() == 'A_Env':
            q_array = []
            for element in queryset:
                if (not element.deja_envoyee) and element.deja_validee:
                    q_array.append(element.id)
            return queryset.filter(pk__in=q_array)

class FactureAdmin(admin.ModelAdmin):
    #list_display = ('Numero_Facture','Etat','Date_Dernier_Rappel','Date_Envoi','Date_Relance1','Date_Relance2', 'Date_Relance3', 'Date_Relance4', 'Date_Relance5', 'Num_Relance','deja_validee','deja_envoyee','deja_payee','Nom_Affaire', 'Montant_Facture_HT', 'ID_Payeur','Date_Echeance1', 'Date_Relance', 'Date_Dernier_Rappel')
    list_display = ('Numero_Facture', 'Etat', 'deja_validee', 'deja_envoyee', 'deja_payee', 'Nom_Affaire',
                    'Montant_Facture_HT', 'Reste_A_Payer','ID_Payeur', 'Date_Echeance1', 'Num_Relance', 'Date_Dernier_Rappel')
    seach_fiels = ('Nom_Affaire__Startswith')
    list_filter = (A_Relancer_Filter,A_Envoyer_Filter,'Etat_Paiement','Etat','Nom_Affaire',)
    list_editable = ('deja_payee',)
    #list_per_page = 12
    formfield_overrides = {models.DecimalField: {
            'widget': forms.TextInput(attrs={'style': 'text-align:right;', }),
        },
    }
    localized_fields = ('Honoraire_Affaire', 'Reste_Affaire','Montant_Facture_HT','Date_Prev_Affaire',)

    change_form_template = 'bdd/Modification_Facture.html'
    change_list_template = 'admin/change_list2.html'
    form = FactureFormModif

    totalsum_list = ('Montant_Facture_HT','Reste_A_Payer')
    unit_of_measure = ""
    totalsum_decimal_places = 2
    change_list_template = 'bdd/Liste_Affaires.html'

    def changelist_view(self, request, extra_context=None):
        response = super(FactureAdmin, self).changelist_view(request, extra_context)
        if not hasattr(response, "context_data") or "cl" not in response.context_data:
            return response
        filtered_query_set = response.context_data["cl"].queryset
        extra_context = extra_context or {}
        extra_context["totals"] = {}
        extra_context["unit_of_measure"] = self.unit_of_measure
        for elem in self.totalsum_list:
            try:
                self.model._meta.get_field(elem)  # Checking if elem is a field
                total = filtered_query_set.aggregate(totalsum_field=Sum(elem))["totalsum_field"]
                if total is not None:
                    extra_context["totals"][label_for_field(elem, self.model, self)] = round(total, self.totalsum_decimal_places)
            except FieldDoesNotExist:  # maybe it's a property
                if hasattr(self.model, elem):
                    total = 0
                    for f in filtered_query_set:
                        try:
                            total += getattr(f, elem, 0)
                        except TypeError:
                            total += getattr(f, elem, 0)()
                    extra_context["totals"][label_for_field(elem, self.model, self)] = round(total, self.totalsum_decimal_places)
        response.context_data.update(extra_context)
        return response

    actions = ['delete_selected']

    #A mettre pour éviter les suppressions de factures validées
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.custom_delete()
        messages.add_message(request, messages.WARNING, "Seules les factures non validées ont été supprimées.")

    '''Une autre version qui marche
        def delete_queryset(self, request, queryset):
            q_array = []
            for element in queryset:
                if element.deja_validee == False:
                    q_array.append(element.id)
            super().delete_queryset(request, queryset.filter(pk__in=q_array))'''

    def Date_Prev_Affaire_aff(self,obj):
        return obj.Date_Prev_Affaire().strftime('%d/%m/%Y')

    Date_Prev_Affaire_aff.short_description = "Date prévisionnelle actuelle de l'affaire"

    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            self.readonly_fields = ()
            return CreationFactureForm
        elif obj.deja_validee:
            self.readonly_fields = ('Avoirs_Lies','Montants_Avoirs_Lies','Date_Prev_Affaire', 'Honoraire_Affaire', 'Reste_Affaire', 'Num_Affaire')
            return FactureForm
        self.readonly_fields = ('Avoirs_Lies','Montants_Avoirs_Lies','Date_Prev_Affaire', 'Honoraire_Affaire', 'Reste_Affaire', 'Num_Affaire')
        return super().get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj = None):
        if not obj:
            return []
        elif obj.deja_validee:
            return ['Numero_Facture','Nom_Affaire','ID_Payeur','ID_Envoi_Facture','ID_Pilote',
                  'Descriptif','Montant_Facture_HT','Taux_TVA','Solde_Pour_Avoir_Eventuel','Avoirs_Lies','Montants_Avoirs_Lies','Facture_Liee','Date_Facture','Modalites_Paiement']
        elif obj.Num_Relance == 0 and not obj.deja_validee:
            return ('Date_Prev_Affaire_aff','Honoraire_Affaire', 'Reste_Affaire', 'Num_Affaire','Modalites_Paiement',)
        else:
            return []

    def response_add(self, request, obj, post_url_continue=None):
        id = obj.id
        url = '/admin/bdd/facture/{}/change'.format(id)
        return redirect(url)

    def fetch_resources(uri, rel):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
        return path

    def change_view(self,request, object_id, extra_context = None):
        facture = Facture.objects.get(pk=object_id)
        id = facture.ID_Affaire_id
        affaire = Affaire.objects.get(pk=id)
        reste = affaire.Reste_A_Regler()
        extra_context = extra_context or {}
        extra_context['Num_Facture'] = facture.Numero_Facture
        extra_context['Reste_Affaire'] = reste
        extra_context['Etat'] = facture.deja_validee
        extra_context['Payee'] = facture.deja_payee
        extra_context['Date_Prev'] = facture.Date_Prev_Affaire()
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['show_delete'] = True
        extra_context['relance'] = facture.Num_Relance
        extra_context['instance'] = facture
        if facture.Facture_Avoir == "FA":
            extra_context['FA'] = True
        else:
            extra_context['FA'] = False
        extra_context = extra_context or {}
        return super().change_view(request, object_id, extra_context = extra_context)

    def response_change(self, request, obj):
        if "Supprimer" in request.POST and request.method == 'POST':
            if not obj.deja_validee:
                obj.delete()
            url = '/admin/bdd/facture'
            return redirect(url)

        if "Fermer_DejaValidee" in request.POST and request.method == 'POST':
            url = '/admin/bdd/facture'
            return redirect(url)

        if "Home" in request.POST and request.method == 'POST':
            return redirect('home')
            #return redirect('/admin/bdd')

        if "Creer_Avoir" in request.POST:
            #print(obj.Nb_Avoir(), obj.Solde_Pour_Avoir_Eventuel())
            if obj.deja_envoyee and obj.Solde_Pour_Avoir_Eventuel()>0:
                obj.save()
                idaffaire = obj.ID_Affaire_id
                affaire = Affaire.objects.get(pk=idaffaire)
                idpayeur = affaire.ID_Payeur
                nomaffaire = affaire.Nom_Affaire
                idenvoifacture = affaire.ID_Envoi_Facture
                idpilote = affaire.ID_Pilote
                numfacture = 'FA0001'
                descriptif="Avoir à valoir sur la facture n°{} du {}".format(obj.Numero_Facture,obj.Date_Facture.strftime("%d/%m/%Y"))
                facture = Facture.objects.create(ID_Affaire_id=idaffaire,
                                                 ID_Payeur = idpayeur, Nom_Affaire = nomaffaire,
                                                 ID_Envoi_Facture = idenvoifacture, ID_Pilote = idpilote,
                                                 Numero_Facture = numfacture,
                                                 Facture_Liee=obj.Numero_Facture,
                                                 Montant_Facture_HT = Decimal(-obj.Solde_Pour_Avoir_Eventuel()),
                                                 Taux_TVA = obj.Taux_TVA,
                                                 Descriptif=descriptif )

                id = facture.pk
                url = '/admin/bdd/facture/{}/change'.format(id)
                return redirect(url, pk=id)
            elif obj.Nb_Avoir() >=1 and obj.Solde_Pour_Avoir_Eventuel()<10**-1:
                messages.add_message(request, messages.ERROR,
                                     "Vous ne pouvez pas créer de nouvel avoir pour cette facture car la totalité du montant initial a déjà fait l'objet d'avoir(s) ({})."
                                     .format(obj.Avoirs_Lies()))
                return redirect(".")
            else:
                messages.add_message(request, messages.ERROR,
                                     "La facture n'a pas été envoyée. Vous ne pouvez pas créer d'avoir. Envoyez votre facture d'abord." )
                return redirect(".")

        if "Relancer_Facture" in request.POST and request.method == 'POST':
            if obj.deja_payee:
                messages.add_message(request, messages.ERROR,
                                     "La facture a été payée. Vous ne pouvez pas la relancer.")
                return redirect('.')
            if obj.Num_Relance >= 7:
                num = obj.Num_Relance
                affichage_message_relance(messages, request, num)
                return redirect('.')
            if obj.Num_Relance != 0:
                num = obj.Num_Relance
                affichage_message_relance(messages, request, num)
                try:
                    obj.save()

                    facture = get_object_or_404(Facture, pk=obj.pk)
                    affaire = Affaire.objects.get(pk=obj.ID_Affaire_id)
                    mission = Offre_Mission.objects.get(pk = affaire.ID_Mission_id)
                    ingeprev = Ingeprev.objects.get(Nom = 'INGEPREV')

                    # Création du pdf dans media
                    data = {}
                    data['facture'] = facture
                    data['Ref_Affaire'] = affaire.Ref_Affaire
                    data['affaire'] = affaire
                    data['Date_Echeance'] = facture.Date_Echeance1()
                    data['Montant_TTC'] = facture.Montant_Facture_TTC()
                    data['ingeprev'] = ingeprev
                    data['mission'] = mission
                    data['date'] = date.today()
                    data['nb']= facture.Nb_Avoir()
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

                    # Création de l'email prérempli
                    message = message_relance(facture)
                    typeaction = 'Relance{}'.format(facture.Num_Relance)
                    idfacture = facture.id
                    sujet = 'Relance {} Facture Ingeprev'.format(facture.Num_Relance)
                    From = settings.DEFAULT_FROM_EMAIL

                    source_html = 'bdd/Visualisation_Facture2.html'
                    fichier = DOSSIER + 'factures/{}.pdf'.format(facture.Numero_Facture)
                    creer_html_to_pdf(source_html, fichier, data)

                    if facture.Num_Relance <= 3:
                        RAR = facture.Num_RAR
                    else:
                        RAR = facture.Num_RAR_Demeure
                    Suivi = facture.Num_Suivi

                    email = InfoEmail.objects.create(From = From, To=facture.Email_Facture, Message=message,
                                                     Subject=sujet, RAR = RAR, Suivi = Suivi,
                                                     ID_Facture=idfacture, Type_Action=typeaction)

                    #Récupération de la facture pdf
                    chemin = Path(DOSSIER + 'factures/{}.pdf'.format(facture.Numero_Facture))
                    with chemin.open(mode='rb') as f:
                        Attachment.objects.create(file=File(f, name=chemin.name), message=email, nom = 'Facture')

                    #Récupération des avoirs liés pdf éventuels
                    nb = facture.Nb_Avoir()
                    if nb >= 1:
                        L = facture.Avoirs_Lies()
                        for k in range(len(L)):
                            x = L[k]
                            avoir = Facture.objects.get(Numero_Facture = x)
                            data2 = {}
                            data2['facture'] = avoir
                            data2['Ref_Affaire'] = affaire.Ref_Affaire
                            data2['affaire'] = affaire
                            data2['Date_Echeance'] = avoir.Date_Echeance1()
                            data2['Montant_TTC'] = avoir.Montant_Facture_TTC()
                            data2['ingeprev'] = ingeprev
                            data2['mission'] = mission
                            data2['date'] = date.today()
                            if avoir.Facture_Avoir == "FA":
                                data2['FA'] = True
                            else:
                                data2['FA'] = False
                            if adresses_identiques(avoir):
                                data2['identiques'] = True
                            else:
                                data2['identiques'] = False
                            if adresses_completes_identiques(avoir):
                                data2['completes_identiques'] = True
                            else:
                                data2['completes_identiques'] = False
                            source_html = 'bdd/Visualisation_Facture2.html'
                            fichier = DOSSIER + 'factures/{}.pdf'.format(avoir.Numero_Facture)
                            creer_html_to_pdf(source_html, fichier, data2)
                            chemin = Path(DOSSIER + 'factures/{}.pdf'.format(x))
                            with chemin.open(mode='rb') as f:
                                Attachment.objects.create(file=File(f, name=chemin.name), message=email, nom='Avoir')

                    #Création des lettres de relance
                    if facture.Num_Relance >= 2:
                        source_html = 'bdd/Lettre_Relance2.html'
                        fichier = DOSSIER + 'relances/Relance2-{}.pdf'.format(facture.Numero_Facture)
                        creer_html_to_pdf(source_html, fichier, data)
                        chemin = Path(DOSSIER + 'relances/Relance2-{}.pdf'.format(facture.Numero_Facture))
                        with chemin.open(mode='rb') as f:
                            Attachment.objects.create(file=File(f, name=chemin.name), message=email, nom = 'Lettre de Relance 2')
                    if facture.Num_Relance == 4:
                        for k in range(3,facture.Num_Relance):
                            source_html = 'bdd/Lettre_Relance{}.html'.format(k)
                            fichier = DOSSIER + 'relances/Relance{}-{}.pdf'.format(k,facture.Numero_Facture)
                            creer_html_to_pdf(source_html, fichier, data)
                            chemin = Path(DOSSIER + 'relances/Relance{}-{}.pdf'.format(k,facture.Numero_Facture))
                            with chemin.open(mode='rb') as f:
                                Attachment.objects.create(file=File(f, name=chemin.name), message=email, nom = 'Lettre de Relance {}'.format(k))
                    elif facture.Num_Relance == 5 or facture.Num_Relance == 6:
                        for k in range(3,5):
                            source_html = 'bdd/Lettre_Relance{}.html'.format(k)
                            fichier = DOSSIER + 'relances/Relance{}-{}.pdf'.format(k,facture.Numero_Facture)
                            creer_html_to_pdf(source_html, fichier, data)
                            chemin = Path(DOSSIER + 'relances/Relance{}-{}.pdf'.format(k,facture.Numero_Facture))
                            with chemin.open(mode='rb') as f:
                                Attachment.objects.create(file=File(f, name=chemin.name), message=email, nom = 'Lettre de Relance {}'.format(k))

                    id = email.pk
                    url = '/admin/bdd/infoemail/{}/change'.format(id)
                    return redirect(url, pk=email.pk)

                except(ValueError, TypeError):
                    pass
            return redirect(".")

        if "Valider_Facture" in request.POST:  #Crée la facture (numéro définitif + enregistrement du fichier pdf + rediriger vers envoi mail )
            if not obj.deja_validee:
                try:
                    obj.save()
                    reste = obj.Montant_Facture_HT-obj.Valeur_Reste_Affaire()
                    if obj.Montant_Facture_HT<0:  #Cas d'un avoir
                        num = obj.Facture_Liee
                        qs = Facture.objects.filter(Numero_Facture=num)
                        if qs.count() < 1:
                            messages.error(request,"Le numéro de Facture à lier à l'avoir est incorrect. Validation impossible.")
                            return redirect('.')
                        else:
                            facture=Facture.objects.get(Numero_Facture=num)
                            if facture.Solde_Pour_Avoir_Eventuel()+obj.Montant_Facture_HT<0:
                                messages.error(request,
                                               "Le montant de l'avoir est supérieur au montant restant de la facture ({} euros). Validation impossible."
                                               .format(facture.Solde_Pour_Avoir_Eventuel()))
                                return redirect('.')
                    elif obj.Montant_Facture_HT-obj.Valeur_Reste_Affaire() > 0:
                        messages.error(request,
                                      "Le montant de la facture est supérieur au montant restant à facturer ({} euros). Validation impossible. Si besoin, modifiez le montant des honoraires de l'affaire.".format(obj.Reste_Affaire()))
                        return redirect('.')

                    '''Pour éviter les factures antérieures à la dernière facture'''
                    if obj.Date_Facture < date_derniere_facture():
                        messages.error(request,
                                       "La date de la facture est antérieure à la date de la dernière facture enregistrée ({}). Validation impossible.".format(date_derniere_facture()))
                        return redirect('.')

                    obj.deja_validee = True
                    obj.Etat = 'VA'
                    obj.Creation_Facture()
                    obj.save()

                    facture = get_object_or_404(Facture, pk=obj.pk)
                    affaire = Affaire.objects.get(pk=obj.ID_Affaire_id)
                    ingeprev = Ingeprev.objects.get(Nom = 'INGEPREV')

                    # Création du pdf de la facture dans media
                    #data['FA'] contiendra True si c'est une facture, False si c'est un avoir
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
                    fichier = DOSSIER + 'factures/{}.pdf'.format(facture.Numero_Facture)
                    creer_html_to_pdf(source_html, fichier, data)
                    #Création du dossier de rangement associé à l'affaire + copie de la facture dedans
                    path = Path(DOSSIER + 'facturation_par_dossier/{}'.format(facture.Num_Affaire()))
                    path.mkdir(parents=True, exist_ok=True)
                    fichier2 = DOSSIER + 'facturation_par_dossier/{}/{}.pdf'.format(facture.Num_Affaire(),facture.Numero_Facture)
                    creer_html_to_pdf(source_html, fichier2, data)

                    # Création de l'email d'envoi de la favture prérempli
                    offre = Offre_Mission.objects.get(pk = affaire.ID_Mission_id)
                    message = message_facture(facture, offre)
                    typeaction = 'Envoi_Facture'
                    idfacture = facture.id
                    if facture.Facture_Avoir == 'FA':
                        sujet = 'Facture Ingéprev'
                    else:
                        sujet = 'Avoir Ingéprev'
                    RAR = facture.Num_RAR
                    From = settings.DEFAULT_FROM_EMAIL
                    email = InfoEmail.objects.create(From = From, To=facture.Email_Facture, Message=message, Subject=sujet,
                                                     ID_Facture=idfacture, Type_Action=typeaction, RAR = RAR)
                    email.save()

                    chemin = Path(DOSSIER + 'factures/{}.pdf'.format(facture.Numero_Facture))
                    with chemin.open(mode='rb') as f:
                        Attachment.objects.create(file=File(f, name=chemin.name), message=email, nom = 'Facture')

                    id = email.pk
                    url = '/admin/bdd/infoemail/{}/change'.format(id)
                    return redirect(url, pk=email.pk)

                except(ValueError, TypeError):
                    pass
            return redirect(".")

        if "Save_Brouillon" in request.POST:
            if not obj.deja_validee:
                try:
                    obj.Remplissage_Facture()
                    obj.save()
                except(ValueError, TypeError):
                    pass
            return redirect(".")

        '''
        if "Apercu_HTML_Facture" in request.POST and request.method == "POST":  #Aperçu du fichier html, rien n'est enregistré
            if not obj.deja_validee:
                try:
                    obj.Remplissage_Facture()
                    obj.save()
                except(ValueError, TypeError):
                    pass
            facture = get_object_or_404(Facture, pk = obj.pk)
            affaire = Affaire.objects.get(pk = obj.ID_Affaire_id)
            ingeprev = Ingeprev.objects.get(Nom='INGEPREV')

            context = {}
            context['facture'] = facture
            context['Ref_Affaire'] = affaire.Ref_Affaire
            context['affaire'] = affaire
            context['Date_Echeance'] = facture.Date_Echeance1()
            context['Montant_TTC'] = facture.Montant_Facture_TTC()
            context['ingeprev'] = ingeprev
            if facture.Facture_Avoir == "FA":
                context['FA'] = True
            else:
                context['FA'] = False
            return render(request, 'bdd/Visualisation_Facture2.html', context)
        '''

        if ("Generer_PDF" in request.POST or "Telecharger_PDF" in request.POST or "Apercu_PDF_Facture" in request.POST) and request.method == 'POST':
            if not obj.deja_validee:
                try:
                    obj.Remplissage_Facture()
                except(ValueError, TypeError):
                    pass
            facture = get_object_or_404(Facture, pk=obj.pk)
            affaire = Affaire.objects.get(pk=obj.ID_Affaire_id)
            ingeprev = Ingeprev.objects.get(Nom='INGEPREV')

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

            if "Generer_PDF" in request.POST:  #Crée un fichier .pdf et l'enregistre dans le dossier media (pas celui de MEDIA_ROOT)
                source_html = 'bdd/Visualisation_Facture2.html'
                template = get_template(source_html)
                html = template.render(data)
                fichier = DOSSIER + 'factures/{}.pdf'.format(facture.Numero_Facture)
                write_to_file = open(fichier, "w+b")
                pisa.CreatePDF(html, dest=write_to_file, link_callback=fetch_resources)
                write_to_file.close()
                return redirect('.')

            if "Apercu_PDF_Facture" in request.POST:  #ouvre la fenètre de téléchargement de chrome - permet de visualiser la facture avant validation
                source_html = 'bdd/Visualisation_Facture2.html'
                filename = '{}.pdf'.format(facture.Numero_Facture)
                fichier = DOSSIER + 'temp/FA0001.pdf'#.format(facture.Numero_Facture)
                template = get_template(source_html)
                html = template.render(data)
                write_to_file = open(fichier, "w+b")
                pisa.CreatePDF(html, dest=write_to_file, link_callback=fetch_resources)
                write_to_file.seek(0)
                pdf = write_to_file.read()
                reponse = HttpResponse(pdf, content_type='application/pdf')
                reponse['Content-Disposition'] = 'filename={}'.format(filename)
                write_to_file.close()
                return reponse
                #return FileResponse(open(fichier, 'rb')) #Ouvre le fichier dans adobe mais ne le télécharge pas
                #return FileResponse(open(fichier,'rb'), as_attachment=True, filename=filename, content_type='application/pdf') #ouvre le fichier dans adobe et le télécharge directement
                #return HttpResponse(pdf, 'application/pdf')
                #En rajoutant formtarget="_blank" dans le bouton je force l'ouverture dans un nouvel onglet

            if "Telecharger_PDF" in request.POST:  #ouvre la fenètre de téléchargement de chrome - permet de visualiser la facture avant validation
                #non utilisé
                source_html = 'bdd/Visualisation_Facture2.html'
                filename = '{}.pdf'.format(facture.Numero_Facture)
                fichier = DOSSIER + '{}.pdf'.format(facture.Numero_Facture)
                template = get_template(source_html)
                html = template.render(data)
                write_to_file = open(fichier, "w+b")
                pisa.CreatePDF(html, dest=write_to_file, link_callback=fetch_resources)
                write_to_file.seek(0)
                #pdf = write_to_file.read()
                write_to_file.close()
                return FileResponse(open(fichier, 'rb'), as_attachment=True, filename=filename,
                                    content_type='application/pdf')  # ouvre le fichier dans adobe et le télécharge directement

        if "Envoyer_Mail" in request.POST:  #Ouvre la fenêtre d'envoi du mail
            if obj.deja_envoyee:
                messages.add_message(request, messages.INFO, "La facture a déjà été envoyée. Vous ne pouvez pas l'envoyer à nouveau.")
                return redirect('.')

            facture = get_object_or_404(Facture, pk=obj.pk)
            affaire = Affaire.objects.get(pk=obj.ID_Affaire_id)
            offre = Offre_Mission.objects.get(pk=affaire.ID_Mission_id)

            #Création du pdf dans media
            data = {}
            data['facture'] = facture
            data['Ref_Affaire'] = affaire.Ref_Affaire
            data['affaire'] = affaire
            data['Date_Echeance'] = facture.Date_Echeance1()
            data['Montant_TTC'] = facture.Montant_Facture_TTC()
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
            fichier = DOSSIER + 'factures/{}.pdf'.format(facture.Numero_Facture)
            creer_html_to_pdf(source_html,fichier, data)

            #Création de l'email prérempli
            offre = Offre_Mission.objects.get(pk=affaire.ID_Mission_id)
            message = message_facture(facture, offre)
            typeaction = 'Envoi_Facture'
            idfacture = facture.id
            if facture.Facture_Avoir == "FA":
                sujet = 'Facture Ingéprev'
            else:
                sujet = 'Avoir Ingéprev'
            From = settings.DEFAULT_FROM_EMAIL
            if facture.Num_Relance < 5:
                RAR = facture.Num_RAR
            elif facture.Num_Relance == 5:
                RAR = facture.Num_RAR_Demeure
            email = InfoEmail.objects.create(From = From, To = facture.Email_Facture, Message = message,
                                             Subject = sujet, ID_Facture = idfacture, Type_Action = typeaction, RAR=RAR)
            email.save()

            chemin = Path(DOSSIER + '/factures/{}.pdf'.format(facture.Numero_Facture))
            with chemin.open(mode = 'rb') as f:
                Attachment.objects.create(file=File(f, name = chemin.name), message=email, nom = "Facture")

            id = email.pk
            url = '/admin/bdd/infoemail/{}/change'.format(id)
            return redirect(url, pk=email.pk)

        return super().response_change(request, obj)

admin.site.register(InfoEmail, InfoEmailAdmin)
admin.site.register(Pilote)
admin.site.register(Client, ClientAdmin)
admin.site.register(Offre_Mission, Offre_MissionAdmin)
admin.site.register(Affaire, AffaireAdmin)
admin.site.register(Facture, FactureAdmin)
admin.site.register(Envoi_Offre, EnvoiOffreAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Envoi_Facture, EnvoiFactureAdmin)
admin.site.register(Compteur_Indice, CompteurIndiceAdmin)
admin.site.register(Ingeprev,IngeprevAdmin)

#admin.site.disable_action('delete_selected')

'''
            if "Apercu_PDF_Nouvelle_Fenetre" in request.POST:  #Ouvre le pdf dans une fenêtre Adobe
                source_html = 'bdd/Visualisation_Facture2.html'
                template = get_template(source_html)
                html = template.render(data)
                result = BytesIO()

                # This part will create the pdf.
                pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                result.close()

                response = HttpResponse(content_type = 'application/pdf')
                response['Content-Disposition'] = 'attachment; filename = {}.pdf'.format(facture.Numero_Facture)
                response.write(pdf)

                return response
        '''
