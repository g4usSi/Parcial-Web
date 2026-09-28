"""Comandos de administración del proyecto académico."""
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_api.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
