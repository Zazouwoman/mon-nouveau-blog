# Generated by Django 4.0.3 on 2022-09-07 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bdd', '0017_alter_ingeprev_code_banque_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingeprev',
            name='Num_Compte',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Numéro de Compte'),
        ),
    ]
