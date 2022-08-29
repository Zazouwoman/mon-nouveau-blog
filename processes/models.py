from django.db import models

class Log(models.Model):
	dt = models.DateTimeField(auto_now_add=True)
	dt_end = models.DateTimeField(null=True,blank=True)
	success = models.BooleanField(null=True,blank=True)

	class Meta:
		abstract = True

class LogBackup(Log):
	fichier = models.CharField(max_length=255,unique=False)
	size = models.IntegerField(null=True,blank=True)
	
	
	
