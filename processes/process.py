if __name__ == "__main__":
	import django
	django.setup()
from datetime import datetime
import tempfile
import subprocess
import os.path
import shutil
from processes import models as proc
from datetime import datetime
from django.utils import timezone

BACKUP_DIR = "/home/claire/Backup/bdd"
BACKUP_SAVE_CMD = "/home/claire/Deltapi/bin/bd_dump.sh"

def bd_backup():
	filename = timezone.now().strftime("%Y%m%d-%H%M%S") + "-bdd.sql.gz"
	with tempfile.TemporaryDirectory() as D:
		temp_filename = D + "/" + filename
		dest_filename = BACKUP_DIR + "/" + filename
		r = subprocess.run([BACKUP_SAVE_CMD,temp_filename])
		sz = os.path.getsize(temp_filename)
		assert sz > 0
		shutil.move(temp_filename,dest_filename)
		sz = os.path.getsize(dest_filename)
		assert sz > 0
		return dest_filename,sz
		
def bd_backup_run():
	l = proc.LogBackup.objects.create()
	filename,sz = bd_backup()
	l.success = sz > 0
	l.fichier = filename
	l.size = sz
	l.dt_end = timezone.now()
	l.save()
	
	


if __name__ == "__main__":
	bd_backup_run()
		
	
