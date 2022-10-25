from django.db import models
from django.utils.safestring import mark_safe
from django.urls import reverse

import processes.process

DOSSIER_BACKUP = processes.process.BACKUP_DIR

class Log(models.Model):
	dt = models.DateTimeField(auto_now_add=True)
	dt_end = models.DateTimeField(null=True,blank=True)
	success = models.BooleanField(null=True,blank=True)

	class Meta:
		abstract = True

class LogBackup(Log):
	fichier = models.CharField(max_length=255,unique=False)
	size = models.IntegerField(null=True,blank=True)

	def Fonction_Nom_Fichier(self):
		return DOSSIER_BACKUP + self.fichier

	def lien(self):
		return mark_safe("<a href='%s' target='_blank'>PDF</a>" % reverse('lien_backup', args=[self.id]))
	
	
	
