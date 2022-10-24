
'''
Code de création de la facture pdf dans la relance de admin

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

                    source_html = 'bdd/Visualisation_Facture2.html'
                    fichier = DOSSIER_PRIVE + 'factures/{}.pdf'.format(facture.Numero_Facture)
                    creer_html_to_pdf(source_html, fichier, data)
'''



