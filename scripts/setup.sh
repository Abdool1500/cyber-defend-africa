#!/usr/bin/env bash
# Sets up a local development environment for the Cyber Defend Africa
# platform. Safe to re-run — does not delete any existing data.
set -e

echo "==> Creating virtual environment (.venv)"
python3 -m venv .venv

echo "==> Installing Python dependencies"
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements-dev.txt

echo "==> Installing JavaScript dependencies"
npm install

if [ ! -f .env ]; then
  echo "==> Creating .env from .env.example"
  cp .env.example .env
  echo "    Edit .env with your Supabase credentials before running migrate."
else
  echo "==> .env already exists, leaving it as-is"
fi

echo "==> Running migrations"
.venv/bin/python manage.py migrate

echo "==> Seeding demo data"
.venv/bin/python manage.py seed_demo_data

echo ""
echo "Setup complete. Next steps:"
echo "  1. Review .env and add your Supabase credentials when ready."
echo "  2. Run: .venv/bin/python manage.py create_initial_superadmin"
echo "  3. Run: .venv/bin/python manage.py runserver"
