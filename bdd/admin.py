# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from pathlib import Path
from django.core.files import File
from django.http import FileResponse
from io import BytesIO
from django.template.loader import get_template
from dateutil.relativedelta import relativedelta
from .models import *
from .forms import *
from . import models
from django.http import HttpResponse
from .fonctions import link_callback
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages, admin
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.utils import label_for_field
from django.db.models import Sum
from django.core.exceptions import FieldDoesNotExist
from django.utils.html import strip_tags

from django.forms.utils import flatatt
from django.urls import reverse
from django.utils.html import format_html

from xhtml2pdf import pisa

from .fonctions import *
# Register your models here.

DOSSIER = 'media/'  #Nom du dossier dans lequel sont enregistrés les factures, lettres de relance
# en mettant media ils sont enregistrés dans F:\media, en mettant '/media/' ils sont enregistrés
# sur le serveur....

#Définition des permissions pour l'affichage ou non dans le menu admin - Choisir entre personne ne voit ou bien seulement les superuse voient
class EnvoiOffreAdmin(admin.ModelAdmin):
    def get_model_perms(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request, *args, **kwargs)

class EnvoiFactureAdmin(admin.ModelAdmin):
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

    '''
    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            self.readonly_fields = ()
            return AttachmentForm
        self.readonly_fields = ('file_link')
        return super().get_form(request, obj, **kwargs)

    def file_link(self, obj):
        fichier = obj.file
        return format_html(
            '<a{} target = "_blank">{}</a>', flatatt({'href': fichier.url}), fichier.name)
    file_link.allow_tags = True

    def __init__(self,*args,**kwargs):
        super(AttachmentAdmin,self).__init__(*args,**kwargs)
        
    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        attachment = Attachment.objects.get(pk = object_id)
        fichier = attachment.file
        url = fichier.url
        extra_context = extra_context or {}
        extra_context['url'] = url

        return super().change_view(request, object_id, extra_context = extra_context)
    '''

class CompteurIndiceAdmin(admin.ModelAdmin):
    def get_model_perms(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request)

#class AttachmentInline(admin.StackedInline):
class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    fields = ['nom','file_link',]
    readonly_fields = ['nom','file_link',]

    def get_model_perms(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request)

    def __init__(self,*args,**kwargs):
        super(AttachmentInline,self).__init__(*args,**kwargs)

class InfoEmailAdmin(admin.ModelAdmin):
    list_display = ('Subject',)
    form = InfoEmailForm
    change_form_template = 'bdd/Creation_Email.html'
    inlines = [AttachmentInline,]

    def get_model_perms(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request)

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
        else:
            form = super().get_form(request, obj, **kwargs)
        return form

    def change_view(self,request, object_id, extra_context = None):
        email = InfoEmail.objects.get(pk = object_id)
        factureid = email.ID_Facture
        facture = Facture.objects.get(pk=factureid)
        facture_form = FactureForm(instance = facture)
        envoifacture = Envoi_Facture.objects.get(pk = facture.ID_Envoi_Facture_id)
        historique_form = FactureHistoriqueForm(instance = facture)
        extra_context = extra_context or {}
        if facture.Num_Relance != 5:
            RAR = facture.Num_RAR
        else:
            RAR = facture.Num_RAR_Demeure
        if RAR == 'A préciser' or RAR == ' ':
            extra_context['RAR'] = False
        else:
            extra_context['RAR'] = True
        envoi_facture_form = EnvoiFactureForm(instance = envoifacture)
        extra_context['facture_form'] = facture_form
        extra_context['relance'] = facture.Num_Relance
        extra_context['envoi_facture_form'] = envoi_facture_form
        extra_context['subject'] = email.Subject
        extra_context['facture'] = facture
        extra_context['envoifacture'] = envoifacture
        extra_context['historique_form'] = historique_form

        if "Relancer" in request.POST:
            num = facture.Num_Relance
            mise_a_jour_relance(facture, num)
            email.delete()
            messages.add_message(request, messages.INFO, 'Relance {} enregistrée avec succès !!'.format(num))
            url = '/admin/bdd/facture/'
            return redirect(url)

        if "Fermer" in request.POST:
            if facture.Num_Relance != 5:
                facture.Num_RAR = 'A préciser'
            elif facture.Num_Relance == 5:
                facture.Num_RAR_Demeure = 'A préciser'
            facture.save()
            messages.add_message(request, messages.INFO, "Aucune relance n'a été effectuée. Opération annulée.")
            email.delete()
            url = '/admin/bdd/facture'
            return redirect(url)

        return super().change_view(request, object_id, extra_context = extra_context)

    def response_change(self, request, obj, extra_context = None):

        if ("Valider_RAR" in request.POST) or ("Mettre_a_jour_RAR" in request.POST):
            if obj.RAR == 'A préciser':
                messages.add_message(request, messages.INFO, 'Vous devez rentrer un numéro de RAR valide !!')
                return redirect('.')

            facture = Facture.objects.get(pk=obj.ID_Facture)
            if facture.Num_Relance == 4:
                facture.Num_RAR = obj.RAR
            elif facture.Num_Relance ==5:
                facture.Num_RAR_Demeure = obj.RAR
            facture.save()
            print('ici',facture.Num_RAR)

            affaire = Affaire.objects.get(pk=facture.ID_Affaire_id)

            # Création du pdf dans media
            data = {}
            data['facture'] = facture
            data['Ref_Affaire'] = affaire.Ref_Affaire
            data['affaire'] = affaire
            data['Date_Echeance'] = facture.Date_Echeance1()
            data['Montant_TTC'] = facture.Montant_Facture_TTC()

            email = InfoEmail.objects.get(pk=obj.pk)
            if facture.Num_Relance == 4:
                if "Mettre_a_jour_RAR" in request.POST:
                    attachment = Attachment.objects.filter(message_id = email.id).filter(nom = "Lettre de Relance 3")
                    attachment.delete()
                source_html = 'bdd/Lettre_Relance3.html'
                fichier = DOSSIER + 'relances/Relance3-{}.pdf'.format(facture.Numero_Facture)
                creer_html_to_pdf(source_html, fichier, data)
                chemin = Path(fichier)
                with chemin.open(mode='rb') as f:
                     Attachment.objects.create(file=File(f, name=chemin.name), message=email, nom = "Lettre de Relance 3")

            if facture.Num_Relance == 5:
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

                email = EmailMessage(Subject, Message, From, [To], attachments = attachments)

                for attach in attach_files:
                    f = settings.MEDIA_URL + attach.file.name
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
            obj.delete()
            messages.add_message(request, messages.INFO, 'Votre email a été envoyé avec succès !!')
            url = '/admin/bdd/facture/'
            return redirect(url)

        return super().response_change(request, obj, extra_context)

class ClientAdmin(admin.ModelAdmin):
    list_display = ("Denomination_Sociale", "SIRET", "Adresse", "CP", "Ville", 'Total_Affaire')
    search_fields = ("Denomination_Sociale__startswith",)
    form = ClientForm

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
    list_display = ("Nom_Mission", "ID_Payeur", "Adresse", "CP", "Ville","ID_Pilote",'Date_Proposition','Etat')
    search_fields = ("Nom_Mission__startswith",)
    list_filter = ('Etat','ID_Pilote',)
    form = Offre_MissionForm

    class  Meta:
        model = Offre_Mission

    def get_form(self, request, obj=None, **kwargs):
        '''
        if not obj:
            form = Offre_MissionAdminForm
        else:
            form = Offre_MissionForm
            '''
        return super().get_form(request,**kwargs)

    def get_readonly_fields(self, request, obj = None):
        return ['Etat','Date_Acceptation']

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
    title = "Affaire à envoyer"
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
    list_display = ("Nom_Affaire", "ID_Payeur", "Honoraires_Global", 'Reste_A_Regler', 'Solde', 'soldee', "Date_Previsionnelle")
    search_fields = ("Nom_Affaire__startswith",)
    list_filter = (Previsionnel_Filter, ASolder_Filter, 'ID_Pilote',)
    radio_fields = {"Type_Affaire":admin.HORIZONTAL,"Etat": admin.HORIZONTAL}
    list_editable = ('Date_Previsionnelle','soldee',)
    totalsum_list = ('Reste_A_Regler',)
    unit_of_measure = ""
    totalsum_decimal_places = 2
    change_list_template = 'bdd/Liste_Affaires.html'
    form = AffaireForm

    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            return CreationAffaireForm
        return super().get_form(request, obj, **kwargs)

    def get_changelist_form(self, request, **kwargs):
        #self.readonly_fields = ('Solde', )
        return super().get_changelist_form(request, **kwargs)

    class Meta:
        model = Affaire

    def response_add(self, request, obj, post_url_continue=None):
        id = obj.id
        url = '/admin/bdd/affaire/{}/change'.format(id)
        return redirect(url)

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
                total = filtered_query_set.aggregate(totalsum_field=Sum(elem))[
                    "totalsum_field"
                ]
                if total is not None:
                    extra_context["totals"][
                        label_for_field(elem, self.model, self)
                    ] = round(total, self.totalsum_decimal_places)
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
               ('Rel1','1ère relance (email)'),
               ('Rel2','2ème relance (tél)'),
               ('Rel3','3ème relance (courrier)'),
               ('Rel4','4ème relance (RAR)'),
               ('Rel5', 'dernière relance'),)

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

        for k in range(1,6):
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
                if not element.deja_envoyee == True and element.deja_validee:
                    q_array.append(element.id)
            return queryset.filter(pk__in=q_array)

class FactureAdmin(admin.ModelAdmin):
    #list_display = ('Numero_Facture','Etat','Date_Dernier_Rappel','Date_Envoi','Date_Relance1','Date_Relance2', 'Date_Relance3', 'Date_Relance4', 'Date_Relance5', 'Num_Relance','deja_validee','deja_envoyee','deja_payee','Nom_Affaire', 'Montant_Facture_HT', 'ID_Payeur','Date_Echeance1', 'Date_Relance', 'Date_Dernier_Rappel')
    list_display = (
    'Numero_Facture', 'Etat', 'deja_validee', 'deja_envoyee', 'deja_payee', 'Nom_Affaire',
    'Montant_Facture_HT', 'ID_Payeur', 'Date_Echeance1', 'Num_Relance', 'Date_Dernier_Rappel')
    seach_fiels = ('Nom_Affaire__Startswith')
    list_filter = (A_Relancer_Filter,A_Envoyer_Filter,'Etat_Paiement','Etat','Nom_Affaire',)
    list_editable = ('deja_payee',)
    list_per_page = 20

    #Changement ici
    form = FactureForm
    change_form_template = 'bdd/Modification_Facture.html'

    # actions = ['my_action']

    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            self.readonly_fields = ()
            return CreationFactureForm
        self.readonly_fields = ('Honoraire_Affaire', 'Reste_Affaire','Num_Affaire')
        return super().get_form(request, obj, **kwargs)

    '''
    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            form = CreationFactureForm
            self.readonly_fields = ()
        elif obj.Num_Relance == 0 and not obj.deja_validee:
            form = FactureForm
            self.readonly_fields = ('Honoraire_Affaire', 'Reste_Affaire', 'Num_Affaire')
        elif obj.Num_Relance == 0:
            form = VisualisationFactureForm
            self.readonly_fields = ['ID_Payeur', 'ID_Envoi_Facture', 'ID_Pilote', 'Descriptif', 'Montant_Facture_HT','Taux_TVA', 'Date_Facture']
        else:
            form = VisualisationFactureForm
        return form
    '''

    def get_readonly_fields(self, request, obj = None):
        if not obj:
            return []
        elif obj.deja_validee:
            return ['ID_Payeur','ID_Envoi_Facture','ID_Pilote','Descriptif','Montant_Facture_HT', 'Taux_TVA','Date_Facture']
        elif obj.Num_Relance == 0 and not obj.deja_validee:
            return ('Honoraire_Affaire', 'Reste_Affaire', 'Num_Affaire',)
        else:
            return []

    def response_add(self, request, obj, post_url_continue=None):
        id = obj.id
        url = '/admin/bdd/facture/{}/change'.format(id)
        return redirect(url)

    def change_view(self,request, object_id, extra_context = None):
        facture = Facture.objects.get(pk = object_id)
        id = facture.ID_Affaire_id
        affaire = Affaire.objects.get(pk=id)
        reste = affaire.Reste_A_Regler()
        extra_context = extra_context or {}
        extra_context['Reste_Affaire'] = reste
        extra_context['Etat'] = facture.deja_validee
        extra_context['Payee'] = facture.deja_payee
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['relance'] = facture.Num_Relance
        return super().change_view(request, object_id, extra_context = extra_context)

    def response_change(self, request, obj, extra_context = None):
        extra_context = extra_context or {}
        extra_context['Etat'] = obj.Etat

        if "Fermer" in request.POST:
            url = '/admin/bdd/facture'
            return redirect(url)

        if "Home" in request.POST:
            return redirect('home')
            #return redirect('/admin/bdd')

        if "Relancer_Facture" in request.POST:
            if obj.deja_payee:
                messages.add_message(request, messages.INFO,
                                     "La facture a été payée. Vous ne pouvez pas la relancer.")
                return redirect('.')
            if obj.Num_Relance >= 6:
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

                    # Création du pdf dans media
                    data = {}
                    data['facture'] = facture
                    data['Ref_Affaire'] = affaire.Ref_Affaire
                    data['affaire'] = affaire
                    data['Date_Echeance'] = facture.Date_Echeance1()
                    data['Montant_TTC'] = facture.Montant_Facture_TTC()

                    source_html = 'bdd/Lettre_Relance1.html'

                    # Création de l'email prérempli
                    message = message_relance(facture, affaire)
                    typeaction = 'Relance{}'.format(facture.Num_Relance)
                    idfacture = facture.id
                    sujet = 'Relance {} Facture Ingeprev'.format(facture.Num_Relance)
                    if facture.Num_Relance <= 4:
                        RAR = facture.Num_RAR
                    else:
                        RAR = facture.Num_RAR_Demeure

                    if facture.Num_Relance == 1:
                        message = strip_tags(render_to_string(source_html,data))

                    email = InfoEmail.objects.create(To=facture.Email_Facture, Message=message,
                                                     Subject=sujet, RAR = RAR,
                                                     ID_Facture=idfacture, Type_Action=typeaction)
                    if facture.Num_Relance == 1:
                        email.content_subtype = "html"
                    email.save()

                    if facture.Num_Relance == 3:
                        source_html = 'bdd/Lettre_Relance2.html'
                    fichier = DOSSIER + 'relances/Relance1-{}.pdf'.format(facture.Numero_Facture)
                    if facture.Num_Relance == 3:
                        fichier = DOSSIER + 'relances/Relance2-{}.pdf'.format(facture.Numero_Facture)
                    creer_html_to_pdf(source_html, fichier, data)

                    #Récupération de la facture pdf
                    chemin = Path(DOSSIER + 'factures/{}.pdf'.format(facture.Numero_Facture))
                    with chemin.open(mode='rb') as f:
                        Attachment.objects.create(file=File(f, name=chemin.name), message=email, nom = 'Facture')

                    if facture.Num_Relance == 1 or facture.Num_Relance == 5:
                        chemin = Path(DOSSIER + 'relances/Relance1-{}.pdf'.format(facture.Numero_Facture))
                        with chemin.open(mode='rb') as f:
                            Attachment.objects.create(file=File(f, name=chemin.name), message=email, nom = 'Lettre de Relance 1')

                    if facture.Num_Relance == 3:
                        chemin = Path(DOSSIER + 'relances/Relance2-{}.pdf'.format(facture.Numero_Facture))
                        with chemin.open(mode='rb') as f:
                            Attachment.objects.create(file=File(f, name=chemin.name), message=email, nom = 'Lettre de Relance 2')

                    if facture.Num_Relance == 5:
                        for k in [2,3]:
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
                    obj.deja_validee = True
                    obj.Etat = 'VA'
                    obj.Creation_Facture()
                    obj.save()

                    facture = get_object_or_404(Facture, pk=obj.pk)
                    affaire = Affaire.objects.get(pk=obj.ID_Affaire_id)

                    # Création du pdf dans media
                    data = {}
                    data['facture'] = facture
                    data['Ref_Affaire'] = affaire.Ref_Affaire
                    data['affaire'] = affaire
                    data['Date_Echeance'] = facture.Date_Echeance1()
                    data['Montant_TTC'] = facture.Montant_Facture_TTC()

                    source_html = 'bdd/Visualisation_Facture2.html'
                    fichier = DOSSIER + 'factures/{}.pdf'.format(facture.Numero_Facture)
                    creer_html_to_pdf(source_html, fichier, data)

                    # Création de l'email prérempli
                    message = message_facture(facture, affaire)
                    typeaction = 'Envoi_Facture'
                    idfacture = facture.id
                    sujet = 'Facture Ingeprev'
                    RAR = facture.Num_RAR
                    email = InfoEmail.objects.create(To=facture.Email_Facture, Message=message, Subject=sujet,
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

        if "Apercu_HTML_Facture" in request.POST and request.method == "POST":  #Aperçu du fichier html, rien n'est enregistré
            if not obj.deja_validee:
                try:
                    obj.Remplissage_Facture()
                    obj.save()
                except(ValueError, TypeError):
                    pass
            facture = get_object_or_404(Facture, pk = obj.pk)
            affaire = Affaire.objects.get(pk = obj.ID_Affaire_id)

            context = {}
            context['facture'] = facture
            context['Ref_Affaire'] = affaire.Ref_Affaire
            context['affaire'] = affaire
            context['Date_Echeance'] = facture.Date_Echeance1()
            context['Montant_TTC'] = facture.Montant_Facture_TTC()
            return render(request, 'bdd/Visualisation_Facture.html', context)

        if ("Generer_PDF" in request.POST or "Telecharger_PDF" in request.POST or "Apercu_PDF_Facture" in request.POST) and request.method == 'POST':
            if not obj.deja_validee:
                try:
                    obj.Remplissage_Facture()
                    obj.save()
                except(ValueError, TypeError):
                    pass
            facture = get_object_or_404(Facture, pk=obj.pk)
            affaire = Affaire.objects.get(pk=obj.ID_Affaire_id)

            data = {}
            data['facture'] = facture
            data['Ref_Affaire'] = affaire.Ref_Affaire
            data['affaire'] = affaire
            data['Date_Echeance'] = facture.Date_Echeance1()
            data['Montant_TTC'] = facture.Montant_Facture_TTC()

            if "Generer_PDF" in request.POST:  #Crée un fichier .pdf et l'enregistre dans le dossier media (pas celui de MEDIA_ROOT)
                source_html = 'bdd/Visualisation_Facture2.html'
                template = get_template(source_html)
                html = template.render(data)
                fichier = DOSSIER + 'factures/{}.pdf'.format(facture.Numero_Facture)
                write_to_file = open(fichier, "w+b")
                pisa.CreatePDF(html, dest=write_to_file, link_callback=link_callback)
                write_to_file.close()
                return redirect('.')

            if "Apercu_PDF_Facture" in request.POST:  #ouvre la fenètre de téléchargement de chrome - permet de visualiser la facture avant validation
                source_html = 'bdd/Visualisation_Facture2.html'
                filename = '{}.pdf'.format(facture.Numero_Facture)
                fichier = DOSSIER + '{}.pdf'.format(facture.Numero_Facture)
                template = get_template(source_html)
                html = template.render(data)
                write_to_file = open(fichier, "w+b")
                pisa.CreatePDF(html, dest=write_to_file, link_callback=link_callback)
                write_to_file.seek(0)
                pdf = write_to_file.read()
                write_to_file.close()
                #return FileResponse(open(fichier, 'rb')) #Ouvre le fichier dans adobe mais ne le télécharge pas
                #return FileResponse(open(fichier,'rb'), as_attachment=True, filename=filename, content_type='application/pdf') #ouvre le fichier dans adobe et le télécharge directement
                return HttpResponse(pdf, 'application/pdf')
                #En rajoutant formtarget="_blank" dans le bouton je force l'ouverture dans un nouvel onglet

            if "Telecharger_PDF" in request.POST:  #ouvre la fenètre de téléchargement de chrome - permet de visualiser la facture avant validation
                #non utilisé
                source_html = 'bdd/Visualisation_Facture2.html'
                filename = '{}.pdf'.format(facture.Numero_Facture)
                fichier = DOSSIER + '{}.pdf'.format(facture.Numero_Facture)
                template = get_template(source_html)
                html = template.render(data)
                write_to_file = open(fichier, "w+b")
                pisa.CreatePDF(html, dest=write_to_file, link_callback=link_callback)
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

            #Création du pdf dans media
            data = {}
            data['facture'] = facture
            data['Ref_Affaire'] = affaire.Ref_Affaire
            data['affaire'] = affaire
            data['Date_Echeance'] = facture.Date_Echeance1()
            data['Montant_TTC'] = facture.Montant_Facture_TTC()

            source_html = 'bdd/Visualisation_Facture2.html'
            fichier = DOSSIER + 'factures/{}.pdf'.format(facture.Numero_Facture)
            creer_html_to_pdf(source_html,fichier, data)

            #Création de l'email prérempli
            message = message_facture(facture, affaire)
            typeaction = 'Envoi_Facture'
            idfacture = facture.id
            sujet = 'Facture Ingeprev'
            if facture.Num_Relance < 5:
                RAR = facture.Num_RAR
            elif facture.Num_Relance == 5:
                RAR = facture.Num_RAR_Demeure
            email = InfoEmail.objects.create(To = facture.Email_Facture, Message = message,
                                             Subject = sujet, ID_Facture = idfacture, Type_Action = typeaction, RAR=RAR)
            email.save()

            chemin = Path(DOSSIER + '/factures/{}.pdf'.format(facture.Numero_Facture))
            with chemin.open(mode = 'rb') as f:
                Attachment.objects.create(file=File(f, name = chemin.name), message=email, nom = "Facture")

            id = email.pk
            url = '/admin/bdd/infoemail/{}/change'.format(id)
            return redirect(url, pk=email.pk)

        return super().response_change(request, obj, extra_context = extra_context)

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
admin.site.register(Entreprise)
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
