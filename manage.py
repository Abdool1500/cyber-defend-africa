#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # `manage.py test` always runs against config.settings.test (in-memory
    # DB, no dependence on live Supabase credentials) regardless of what's
    # configured for local development.
    default_settings = 'config.settings.test' if 'test' in sys.argv[1:2] else 'config.settings.development'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', default_settings)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
