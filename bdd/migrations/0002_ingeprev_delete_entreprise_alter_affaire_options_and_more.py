# Generated by Django 4.0.3 on 2022-04-24 22:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bdd', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingeprev',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nom', models.CharField(blank=True, max_length=50, verbose_name='Nom de la societe')),
                ('SIRET', models.CharField(blank=True, max_length=50, verbose_name='N° de SIRET')),
                ('Adresse', models.CharField(blank=True, max_length=500)),
                ('Complement_Adresse', models.CharField(blank=True, max_length=500, verbose_name="Complément d'Adresse")),
                ('CP', models.CharField(blank=True, max_length=5, validators=[django.core.validators.RegexValidator(message='le code postal doit être composé de 5 chiffres.', regex='^[0-9]+$')], verbose_name='Code postal')),
                ('Ville', models.CharField(blank=True, max_length=150)),
                ('Type_Societe', models.CharField(blank=True, max_length=150, verbose_name='Statut juridique')),
                ('IBAN', models.CharField(blank=True, max_length=150, verbose_name='IBAN')),
                ('Code_APE', models.CharField(blank=True, max_length=150, verbose_name='Code APE')),
                ('Capital', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=15, verbose_name='Capital')),
                ('Num_TVA', models.CharField(blank=True, max_length=150, verbose_name='N° de TVA Intercommunautaire')),
                ('Email', models.EmailField(blank=True, max_length=70)),
                ('Tel', models.CharField(blank=True, max_length=16, validators=[django.core.validators.RegexValidator(message='Un numero de téléphone est attendu.', regex='^\\+?1?\\d{8,15}$')], verbose_name='Numéro de Téléphone')),
                ('Site_Web', models.URLField(blank=True, max_length=300)),
                ('Facebook', models.URLField(blank=True, max_length=300)),
                ('Twitter', models.URLField(blank=True, max_length=300)),
                ('Linkedin', models.URLField(blank=True, max_length=300)),
            ],
            options={
                'verbose_name_plural': '6. INGEPREV',
            },
        ),
        migrations.DeleteModel(
            name='Entreprise',
        ),
        migrations.AlterModelOptions(
            name='affaire',
            options={'verbose_name_plural': '2. Affaires'},
        ),
        migrations.AlterModelOptions(
            name='client',
            options={'ordering': ['Denomination_Sociale'], 'verbose_name_plural': '4. Clients'},
        ),
        migrations.AlterModelOptions(
            name='facture',
            options={'verbose_name_plural': '3. Factures'},
        ),
        migrations.AlterModelOptions(
            name='offre_mission',
            options={'ordering': ['Nom_Mission'], 'verbose_name_plural': '1. Offres de Mission'},
        ),
        migrations.AlterModelOptions(
            name='pilote',
            options={'ordering': ['Nom'], 'verbose_name_plural': '5. Pilotes'},
        ),
        migrations.AlterField(
            model_name='client',
            name='Tel_Representant',
            field=models.CharField(blank=True, max_length=16, validators=[django.core.validators.RegexValidator(message='Un numero de téléphone est attendu.', regex='^\\+?1?\\d{8,15}$')], verbose_name='Numéro de téléphone'),
        ),
        migrations.AlterField(
            model_name='envoi_facture',
            name='Tel_Contact',
            field=models.CharField(blank=True, max_length=16, validators=[django.core.validators.RegexValidator(message='Un numero de téléphone est attendu.', regex='^\\+?1?\\d{8,15}$')], verbose_name='Numéro de téléphone'),
        ),
        migrations.AlterField(
            model_name='envoi_offre',
            name='Tel_Contact',
            field=models.CharField(blank=True, max_length=16, validators=[django.core.validators.RegexValidator(message='Un numero de téléphone est attendu.', regex='^\\+?1?\\d{8,15}$')], verbose_name='Numéro de téléphone'),
        ),
        migrations.AlterField(
            model_name='facture',
            name='Tel_Portable_Pilote',
            field=models.CharField(blank=True, max_length=16, validators=[django.core.validators.RegexValidator(message='Un numero de téléphone est attendu.', regex='^\\+?1?\\d{8,15}$')], verbose_name='Numéro de Portable'),
        ),
        migrations.AlterField(
            model_name='pilote',
            name='Tel_Fixe',
            field=models.CharField(blank=True, max_length=16, validators=[django.core.validators.RegexValidator(message='Un numero de téléphone est attendu.', regex='^\\+?1?\\d{8,15}$')], verbose_name='numéro de Fixe'),
        ),
        migrations.AlterField(
            model_name='pilote',
            name='Tel_Portable',
            field=models.CharField(blank=True, max_length=16, validators=[django.core.validators.RegexValidator(message='Un numero de téléphone est attendu.', regex='^\\+?1?\\d{8,15}$')], verbose_name='Numéro de Portable'),
        ),
    ]
