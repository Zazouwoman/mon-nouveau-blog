
from django import forms
from multiupload.fields import MultiFileField

from .models import *

class InfoEmailForm(forms.ModelForm):
    class Meta:
        model = InfoEmail
        #fields = '__all__'
        fields = ['From','To','Subject','Message']

    def __init__(self, *args, **kwargs):
        super(InfoEmailForm, self).__init__(*args, **kwargs)

    Pieces_Jointes = MultiFileField(label = 'Pièces jointes', min_num=0, max_num=5, max_file_size=1024 * 1024 * 5)

    def save(self, commit=True):
        instance = super(InfoEmailForm, self).save(commit)
        for each in self.cleaned_data['Pieces_Jointes']:
            Attachment.objects.create(file=each, message=instance)

        return instance

class RelanceForm2(forms.ModelForm):
    class Meta:
        model = InfoEmail
        fields = ('Subject',)

    def __init__(self, *args, **kwargs):
        super(RelanceForm2, self).__init__(*args, **kwargs)
        self.fields['Subject'].widget.attrs['readonly'] = True

class RelanceForm3(forms.ModelForm):
    class Meta:
        model = InfoEmail
        fields = ('Subject',)

    def __init__(self, *args, **kwargs):
        super(RelanceForm3, self).__init__(*args, **kwargs)
        self.fields['Subject'].widget.attrs['readonly'] = True

    #Pieces_Jointes = MultiFileField(label='Pièces jointes', min_num=0, max_num=3, max_file_size=1024 * 1024 * 5)

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

    Pieces_Jointes = MultiFileField(label = 'Pièces jointes', min_num=0, max_num=10, max_file_size=1024 * 1024 * 5)

    def save(self, commit=True):
        instance = super(RelanceForm4, self).save(commit)
        for each in self.cleaned_data['Pieces_Jointes']:
            Attachment.objects.create(file=each, message=instance)
        return instance

class RelanceForm5(forms.ModelForm):
    class Meta:
        model = InfoEmail
        fields = ['Subject', 'RAR']

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
    class Meta:
        model = Affaire
        exclude = ['soldee','ID_Client_Cache','Type_Dossier','Indice_Dossier','ID_Mission','Etat']
        localized_fields = ('Honoraires_Global',)

    def __init__(self, *args, **kwargs):
        super(AffaireForm, self).__init__(*args, **kwargs)
        #self.fields['Honoraires_Global_str_'].widget.attrs['readonly'] = True
        self.fields['Ref_Affaire'].widget.attrs['readonly'] = True

class CreationFactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['ID_Affaire']

    def __init__(self, *args, **kwargs):
        super(CreationFactureForm, self).__init__(*args, **kwargs)

class FactureHistoriqueForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['Numero_Facture', 'Date_Envoi', 'Date_Relance1', 'Date_Relance2', 'Date_Relance3', 'Date_Relance4', 'Num_RAR','Num_RAR_Demeure']
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
        fields = ['Numero_Facture','ID_Affaire','Nom_Affaire','ID_Payeur','ID_Envoi_Facture','ID_Pilote',
                  'Descriptif','Montant_Facture_HT','Taux_TVA','Date_Facture','Facture_Liee']
        localized_fields = ('Montant_Facture_HT',)

    Date_Prev = forms.DateField(label="Nouvelle date prévisionnelle de l'affaire", required=False)

    def __init__(self, *args, **kwargs):
        super(FactureFormModif, self).__init__(*args, **kwargs)
        self.fields['Numero_Facture'].widget.attrs['readonly'] = True
        self.fields['Nom_Affaire'].widget.attrs['readonly'] = True
        #self.fields['Modalites_Paiement'].widget.attrs['readonly'] = True
        self.fields['ID_Affaire'].widget = forms.HiddenInput()
        id=self.initial['ID_Affaire']
        affaire=Affaire.objects.get(pk=id)
        self.fields['Date_Prev'].initial = affaire.Date_Previsionnelle

    def save(self, commit=True):
        instance = super(FactureFormModif, self).save(commit)
        facture = Facture.objects.get(pk=instance.pk)
        affaire = Affaire.objects.get(pk=facture.ID_Affaire_id)
        nouvdate = self.cleaned_data['Date_Prev']
        affaire.Date_Previsionnelle = nouvdate
        facture.save()
        affaire.save()
        instance.save()
        return instance

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

    def __init__(self, *args, **kwargs):
        super(EnvoiFactureForm, self).__init__(*args, **kwargs)
        fields = self.fields
        for x in fields:
            self.fields[x].widget.attrs['readonly'] = True






