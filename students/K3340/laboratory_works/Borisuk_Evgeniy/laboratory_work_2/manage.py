"""Управление проектом Django."""

import os
import sys


def main() -> None:
    """Запускает команду управления Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project_borisuk.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
