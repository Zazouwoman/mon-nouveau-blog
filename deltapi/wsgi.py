"""
WSGI config for deltapi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application
#Ligne suivante pour le développement sur le site de Benoit
sys.path.insert(0,"/home/claire/Deltapi")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deltapi.settings')

application = get_wsgi_application()
