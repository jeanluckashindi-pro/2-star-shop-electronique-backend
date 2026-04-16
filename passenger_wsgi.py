import os
import sys

# Chemin du projet sur le serveur
PROJECT_DIR = '/home/neyba/public_html/2starshop/backend'
sys.path.insert(0, PROJECT_DIR)

# Définir le module de settings Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Importer l'application WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
