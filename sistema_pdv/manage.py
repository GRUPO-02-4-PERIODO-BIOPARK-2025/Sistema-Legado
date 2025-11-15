#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_pdv.settings")
    try:
        from django.core.management import execute_from_command_line
    except Exception:
        # Placeholder manage.py — install Django to run for real
        raise
    execute_from_command_line(sys.argv)
