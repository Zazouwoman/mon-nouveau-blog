from django.contrib import admin
import processes.models as proc

@admin.register(proc.LogBackup)
class LogBackupAdmin(admin.ModelAdmin):
	list_display = [ "dt","success","dt_end","fichier","size" ]
	
