import django
django.setup()

from django.conf import settings
import bdd.models as BDD

print("test nom fichier facture")
facture = BDD.Facture.objects.latest("id")
print(facture)
print(facture.Fonction_Nom_Fichier_Facture())


