import os
import sys

from django.core.management import execute_from_command_line

# cd students/K3340/Levakhin_Lev/laboratory_work_3
# .venv\Scripts\activate
# python manage.py runserver
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    execute_from_command_line(sys.argv)
