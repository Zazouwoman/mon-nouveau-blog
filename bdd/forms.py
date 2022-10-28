
from django import forms
from multiupload.fields import MultiFileField

from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget, RelatedFieldWidgetWrapper
from django.contrib.admin import site as admin_site

from .models import *

class InfoEmailForm(forms.ModelForm):
    class Meta:
        model = InfoEmail
        #fields = '__all__'
        fields = ['From','To','Copie1','Copie2','Copie3','Subject','Message']

    def __init__(self, *args, **kwargs):
        super(InfoEmailForm, self).__init__(*args, **kwargs)
        self.fields['From'].widget.attrs['readonly'] = True

    Pieces_Jointes = MultiFileField(label = 'Pièces jointes', min_num=0, max_num=5, max_file_size=1024 * 1024 * 5)

    def save(self, commit=True):
        instance = super(InfoEmailForm, self).save(commit)
        for each in self.cleaned_data['Pieces_Jointes']:
            Attachment.objects.create(file=each, message=instance)

        return instance

class RelanceForm2(forms.ModelForm):
    class Meta:
        model = InfoEmail
        fields = ['Subject','Suivi']

    def __init__(self, *args, **kwargs):
        super(RelanceForm2, self).__init__(*args, **kwargs)
        self.fields['Subject'].widget.attrs['readonly'] = True

    Pieces_Jointes = MultiFileField(label='Pièces jointes', min_num=0, max_num=3, max_file_size=1024 * 1024 * 5)

    def save(self, commit=True):
        instance = super(RelanceForm2, self).save(commit)
        for each in self.cleaned_data['Pieces_Jointes']:
            Attachment.objects.create(file=each, message=instance)
        return instance

'''class RelanceForm3(forms.ModelForm):
    class Meta:
        model = InfoEmail
        fields = ('Subject',)

    def __init__(self, *args, **kwargs):
        super(RelanceForm3, self).__init__(*args, **kwargs)
        self.fields['Subject'].widget.attrs['readonly'] = True
    
    # Pieces_Jointes = MultiFileField(label='Pièces jointes', min_num=0, max_num=3, max_file_size=1024 * 1024 * 5)
        
    def save(self, commit=True):
        instance = super(RelanceForm3, self).save(commit)
        for each in self.cleaned_data['Pieces_Jointes']:
            Attachment.objects.create(file=each, message=instance)
        return instance
'''

class RelanceForm3(forms.ModelForm):
    class Meta:
        model = InfoEmail
        fields = ['Subject', 'RAR']

    def __init__(self, *args, **kwargs):
        super(RelanceForm3, self).__init__(*args, **kwargs)
        self.fields['Subject'].widget.attrs['readonly'] = True

    Pieces_Jointes = MultiFileField(label = 'Pièces jointes', min_num=0, max_num=10, max_file_size=1024 * 1024 * 5)

    def save(self, commit=True):
        instance = super(RelanceForm3, self).save(commit)
        for each in self.cleaned_data['Pieces_Jointes']:
            Attachment.objects.create(file=each, message=instance)
        return instance

class RelanceForm4(forms.ModelForm):
    class Meta:
        model = InfoEmail
        fields = ['Subject', 'RAR']

    def __init__(self, *args, **kwargs):
        super(RelanceForm4, self).__init__(*args, **kwargs)
        self.fields['Subject'].widget.attrs['readonly'] = True

class RelanceForm5(forms.ModelForm):
    class Meta:
        model = InfoEmail
        fields = ('Subject',)

    def __init__(self, *args, **kwargs):
        super(RelanceForm5, self).__init__(*args, **kwargs)
        self.fields['Subject'].widget.attrs['readonly'] = True

class RelanceForm6(forms.ModelForm):
    class Meta:
        model = InfoEmail
        fields = ('Subject',)

    def __init__(self, *args, **kwargs):
        super(RelanceForm6, self).__init__(*args, **kwargs)
        self.fields['Subject'].widget.attrs['readonly'] = True

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ['Type_Dossier','Indice_Dossier']
    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        self.fields['Numero_Client'].widget.attrs['readonly'] = True

class Offre_MissionCreationForm(forms.ModelForm):
    class Meta:
        model = Offre_Mission
        fields = ['Ref_Mission','Nom_Mission','Adresse','CP','ID_Payeur','ID_Envoi_Offre','ID_Client_Cache','ID_Apporteur',
                  'Honoraires_Proposes','Date_Proposition','Descriptif','ID_Pilote']
        #exclude = ['Type_Dossier','Indice_Dossier','Etat','Date_Acceptation']
    def __init__(self, *args, **kwargs):
        super(Offre_MissionCreationForm, self).__init__(*args, **kwargs)
        self.fields['Ref_Mission'].widget.attrs['readonly'] = True

class Offre_MissionForm(forms.ModelForm):
    class Meta:
        model = Offre_Mission
        #fields = ['Ref_Mission','Nom_Mission','Adresse','CP','ID_Payeur','ID_Envoi_Offre','ID_Client_Cache','ID_Apporteur',
        #          'Honoraires_Proposes','Date_Proposition','Date_Acceptation','Descriptif','Etat', 'ID_Pilote']
        exclude = ['Type_Dossier','Indice_Dossier']
        localized_fields = ('Honoraires_Proposes',)
    def __init__(self, *args, **kwargs):
        super(Offre_MissionForm, self).__init__(*args, **kwargs)
        self.fields['Ref_Mission'].widget.attrs['readonly'] = True

class CreationAffaireForm(forms.ModelForm):
     class Meta:
         model = Affaire
         fields = ['ID_Mission']

     def __init__(self, *args, **kwargs):
         super(CreationAffaireForm, self).__init__(*args, **kwargs)
         self.fields['ID_Mission'].queryset = Offre_Mission.objects.filter(Etat="ATT")

class AffaireForm(forms.ModelForm):
    #Cas où le prévisionnel n'a pas encore été créé
    class Meta:
        model = Affaire
        exclude = ['soldee','ID_Client_Cache','Type_Dossier','Indice_Dossier','ID_Mission','Etat','previsionnelcree']
        localized_fields = ('Honoraires_Global',)

    def __init__(self, *args, **kwargs):
        super(AffaireForm, self).__init__(*args, **kwargs)
        #self.fields['Honoraires_Global_str_'].widget.attrs['readonly'] = True
        self.fields['Ref_Affaire'].widget.attrs['readonly'] = True
        self.fields['Date_Creation'].widget.attrs['readonly'] = True
        #self.fields['Date_Creation'].widget.attrs['disabled'] = True
        #self.fields['Date_Creation'].widget.attrs.update({'required':True})

    def clean(self):
        cleaned_data=super().clean()
        datecreation=cleaned_data.get("Date_Creation")
        date1 = self.initial['Date_Creation']
        if date1 != datecreation:
            #self.fields['Date_Creation'] = date1
            raise ValidationError("La date de création ne doit pas être modifiée. Remettez la date initiale qui est le {}.".format(date1))

class AffaireForm2(forms.ModelForm):
    #cas où le prévisionnel a été créé
    class Meta:
        model = Affaire
        exclude = ['soldee','ID_Client_Cache','Type_Dossier','Indice_Dossier','ID_Mission','Etat','previsionnelcree','Date_Previsionnelle']
        localized_fields = ('Honoraires_Global',)

    def __init__(self, *args, **kwargs):
        super(AffaireForm2, self).__init__(*args, **kwargs)
        #self.fields['Honoraires_Global_str_'].widget.attrs['readonly'] = True
        self.fields['Ref_Affaire'].widget.attrs['readonly'] = True
        self.fields['Date_Creation'].widget.attrs['readonly'] = True
        #self.fields['Date_Creation'].widget = AdminDateWidget
        #self.fields['ID_Mission'].widget.attrs['readonly'] = True

class PrevisionnelForm(forms.ModelForm):
    class Meta:
        model = Previsionnel
        fields = '__all__'
        localized_fields = ('Montant_Previsionnel1','Montant_Previsionnel2','Montant_Previsionnel3','Montant_Previsionnel4','Montant_Previsionnel5','Montant_Previsionnel6','Montant_Previsionnel7',)

    #Numero_Phase_En_Cours = forms.CharField(max_length = 2, label="Numéro de la phase en attente de facturation", required = False)

    def __init__(self, *args, **kwargs):
        super(PrevisionnelForm, self).__init__(*args, **kwargs)
        self.fields['ID_Affaire'].widget.attrs['readonly'] = True
        id=self.initial['ID_Affaire']
        previsionnel=Previsionnel.objects.get(ID_Affaire_id=id)
        #self.fields['Numero_Phase_En_Cours'].initial = previsionnel.Echeance_En_Cours()
        #self.fields['Numero_Phase_En_Cours'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super(PrevisionnelForm,self).clean()
        if cleaned_data['Montant_Previsionnel1'] == None:
            cleaned_data['Montant_Previsionnel1'] = 0
        if cleaned_data['Montant_Previsionnel2'] == None:
            cleaned_data['Montant_Previsionnel0'] = 0
        if cleaned_data['Montant_Previsionnel3']== None:
            cleaned_data['Montant_Previsionnel3'] = 0
        if cleaned_data['Montant_Previsionnel4'] == None:
            cleaned_data['Montant_Previsionnel4'] = 0
        if cleaned_data['Montant_Previsionnel5'] == None:
            cleaned_data['Montant_Previsionnel5'] = 0
        if cleaned_data['Montant_Previsionnel6'] == None:
            cleaned_data['Montant_Previsionnel6'] = 0
        if cleaned_data['Montant_Previsionnel7'] == None:
            cleaned_data['Montant_Previsionnel7'] = 0
        Ldate = []
        for k in range(1,8):
            Ldate.append(cleaned_data.get("Date_Previsionnelle{}".format(k)))
        Lmontant = []
        for k in range(1, 8):
            Lmontant.append(cleaned_data.get("Montant_Previsionnel{}".format(k)))
        ordre = True
        for k in range(6):
            if Ldate[k]!=None and Ldate[k+1]!=None and Ldate[k] > Ldate[k+1]:
                ordre = False
        if not ordre:
            raise ValidationError("Les dates ne sont pas dans l'ordre chronologique. Validation Impossible.")
        montant = True
        for k in range(6):
            if Lmontant[k]==0:
                for j in range(k+1,7):
                    if Lmontant[j]!=0:
                        montant = False
                        k1,j1 = k+1,j+1
        if not montant:
            raise ValidationError(
                "Le montant prévisionnel {} est non nul alors que le montant prévisionnel {} est nul. Validation impossible. ".format(
                j1, k1))
        date1 = True
        for k in range(7):
            if Lmontant[k]!=0 and Ldate[k] == None:
                date1 = False
                k2 = k+1
        if not date1:
            raise ValidationError("La date prévionnelle {} est vide alors que le montant prévisionnel {} est non nul. Validation impossible.".format(k2,k2))
        '''
        id = self.initial['ID_Affaire']
        obj = Previsionnel.objects.get(ID_Affaire_id = id)
        honoraires = obj.Montant_Affaire()
        reste = honoraires - sum(Lmontant)

        if reste < 0:
            obj.save()
            obj.Mise_A_Jour_Montant()
            obj.save()
            cleaned_data['Montant_Previsionnel2']=obj.Montant_Previsionnel2
            # previsionnel=Previsionnel.objects.get(pk=obj.id)
            # Mise_A_Jour_Montant(previsionnel)
            raise ValidationError(
                           "La somme des montants prévisionnels est supérieure aux honoraires de l'affaire ({} euros). Validation impossible".format(
                               obj.Montant_Affaire()))
        if reste > 0:
            obj.save()
            obj.Mise_A_Jour_Montant()
            obj.save()
            cleaned_data['Montant_Previsionnel2'] = obj.Montant_Previsionnel2
            #print(obj.Reste(),obj.Montant_Previsionnel2)
            raise ValidationError(
                           "La somme des montants prévisionnels est inférieure aux honoraires de l'affaire ({} euros). Validation impossible.".format(
                               obj.Montant_Affaire()))'''
        return cleaned_data



class CreationFactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['ID_Affaire']

    def __init__(self, *args, **kwargs):
        super(CreationFactureForm, self).__init__(*args, **kwargs)

class FactureHistoriqueForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['Numero_Facture', 'Date_Envoi', 'Date_Relance1', 'Date_Relance2', 'Num_Suivi', 'Date_Relance3', 'Num_RAR', 'Date_Relance4', 'Num_RAR_Demeure']
        #widget = {'style': 'text-align:right;'}

    def __init__(self, *args, **kwargs):
        super(FactureHistoriqueForm, self).__init__(*args, **kwargs)
        self.fields['Numero_Facture'].widget.attrs['readonly'] = True
        self.fields['Date_Envoi'].widget.attrs['readonly'] = True
        self.fields['Date_Relance1'].widget.attrs['readonly'] = True
        self.fields['Date_Relance2'].widget.attrs['readonly'] = True
        self.fields['Date_Relance3'].widget.attrs['readonly'] = True
        self.fields['Date_Relance4'].widget.attrs['readonly'] = True
        self.fields['Num_RAR'].widget.attrs['readonly'] = True
        self.fields['Num_RAR_Demeure'].widget.attrs['readonly'] = True

class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['deja_validee']
        localized_fields = ('Montant_Facture_HT',)

    def __init__(self, *args, **kwargs):
        super(FactureForm, self).__init__(*args, **kwargs)
        self.fields['deja_validee'].widget= forms.HiddenInput()

class FactureFormModif(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['Numero_Facture','ID_Affaire','Nom_Affaire','ID_Payeur','ID_Envoi_Facture','Ref_Client','ID_Pilote',
                  'Descriptif','Montant_Facture_HT','Taux_TVA','Date_Facture','Facture_Liee']
        localized_fields = ('Montant_Facture_HT',)

    #Date_Prev = forms.DateField(label="Nouvelle date prévisionnelle de facturation de l'affaire", required=False)

    def __init__(self, *args, **kwargs):
        super(FactureFormModif, self).__init__(*args, **kwargs)
        self.fields['Numero_Facture'].widget.attrs['readonly'] = True
        self.fields['Nom_Affaire'].widget.attrs['readonly'] = True
        self.fields['ID_Affaire'].widget = forms.HiddenInput()
        id=self.initial['ID_Affaire']
        '''
        try:
            previsionnel=Previsionnel.objects.get(ID_Affaire_id=id)
            idprev = previsionnel.id
            self.fields['Date_Prev'].initial = previsionnel.Prochaine_Date_Previsionnelle()
        except:
            affaire = Affaire.objects.get(pk=id)
            self.fields['Date_Prev'].initial = affaire.Date_Previsionnelle
        self.fields['Date_Prev'].widget.attrs['readonly'] = True'''

    def clean_sku(self):
        if self.instance:
            return self.instance.sku
        else:
            return self.fields['sku']

    def save(self, commit=True):
        instance = super(FactureFormModif, self).save(commit)
        facture = Facture.objects.get(pk=instance.pk)
        affaire = Affaire.objects.get(pk=facture.ID_Affaire_id)
        #nouvdate = self.cleaned_data['Date_Prev']
        #affaire.Date_Previsionnelle = nouvdate
        facture.save()
        affaire.save()
        instance.save()
        return instance

'''Si on veut le popup
class FactureFormModif(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['Numero_Facture','ID_Affaire','Nom_Affaire','ID_Payeur','ID_Envoi_Facture','Ref_Client','ID_Pilote',
                  'Descriptif','Montant_Facture_HT','Taux_TVA','Date_Facture','Facture_Liee']
        localized_fields = ('Montant_Facture_HT',)

    ID_Prev = Facture._meta.get_field('ID_Prev').formfield(
        widget=RelatedFieldWidgetWrapper(
            Facture._meta.get_field('ID_Prev').formfield().widget,
            Facture._meta.get_field('ID_Prev').remote_field,
            admin_site,
            can_add_related=False,
            can_change_related=True,
        )
    )

    #Date_Prev = forms.DateField(label="Nouvelle date prévisionnelle de l'affaire", required=False)

    def __init__(self, *args, **kwargs):
        super(FactureFormModif, self).__init__(*args, **kwargs)
        self.fields['Numero_Facture'].widget.attrs['readonly'] = True
        self.fields['Nom_Affaire'].widget.attrs['readonly'] = True
        #self.fields['Modalites_Paiement'].widget.attrs['readonly'] = True
        self.fields['ID_Affaire'].widget = forms.HiddenInput()
        #self.fields['ID_Prev'].widget.attrs['readonly'] = True
        self.fields['ID_Prev'].widget.attrs['hidden'] = True
        #self.fields['ID_Prev'].widget.attrs['disabled'] = True

    def clean_sku(self):
        if self.instance:
            return self.instance.sku
        else:
            return self.fields['sku']

    def save(self, commit=True):
        instance = super(FactureFormModif, self).save(commit)
        facture = Facture.objects.get(pk=instance.pk)
        affaire = Affaire.objects.get(pk=facture.ID_Affaire_id)
        #nouvdate = self.cleaned_data['Date_Prev']
        #affaire.Date_Previsionnelle = nouvdate
        facture.save()
        affaire.save()
        instance.save()
        return instance
'''

class VisualisationFactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        #fields = ['Numero_Facture', 'Nom_Affaire']
        fields = ['Numero_Facture','Nom_Affaire','ID_Payeur','ID_Envoi_Facture','ID_Pilote','Descriptif','Montant_Facture_HT',
                  'Taux_TVA', 'Date_Facture']
        localized_fields = ('Montant_Facture_HT',)
        readonly_fields = ['Reste_A_Payer','Avoirs_Lies']

    def __init__(self, *args, **kwargs):
        super(VisualisationFactureForm, self).__init__(*args, **kwargs)
        fields = self.fields
        for x in fields:
            self.fields[x].widget.attrs['readonly'] = True

    def clean_sku(self):
        if self.instance:
            return self.instance.sku
        else:
            return self.fields['sku']

class EnvoiFactureForm(forms.ModelForm):
    class Meta:
        model = Envoi_Facture
        fields = '__all__'

    '''
    def __init__(self, *args, **kwargs):
        super(EnvoiFactureForm, self).__init__(*args, **kwargs)
        fields = self.fields
        for x in fields:
            self.fields[x].widget.attrs['readonly'] = True
    '''

    def clean(self):
        cleaned_data = super().clean()
        delais = cleaned_data.get("Delais_Paiement")
        fin = cleaned_data.get("Fin_Mois")
        if not (delais == '30' or (delais == '60' and fin == 'Non')):
            raise ValidationError('Options possibles pour les délais de paiement : 30 jours, 30 jours fin de mois, 60 jours')
            #self.add_error('Delais_Paiement',msg)
            #self.add_error('Fin_Mois',msg)






