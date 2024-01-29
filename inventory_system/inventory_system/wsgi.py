"""
WSGI config for inventory_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'C:/Users/Gennifer Motsumi/Desktop/projects/Hackathon/inventory_system/inventory_system/wsgi.py')

application = get_wsgi_application()

