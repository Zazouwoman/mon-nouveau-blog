# Generated by Django 4.0.5 on 2022-08-29 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processes', '0002_logbackup_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logbackup',
            name='fichier',
            field=models.CharField(max_length=255),
        ),
    ]
