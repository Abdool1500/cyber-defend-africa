#!/usr/bin/env bash
# Runs the full test suite (Python + JavaScript) and the same checks CI runs.
set -e

echo "==> Django system check"
.venv/bin/python manage.py check

echo "==> Checking for missing migrations"
.venv/bin/python manage.py makemigrations --check --dry-run

echo "==> Running Django tests"
.venv/bin/python manage.py test

echo "==> Running Jest tests"
npm test

echo ""
echo "All checks passed."
