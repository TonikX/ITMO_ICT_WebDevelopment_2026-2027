"""Точка входа WSGI."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project_borisuk.settings")
application = get_wsgi_application()
