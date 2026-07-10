# Cyber Defend Africa LTD — Platform

Corporate website, Cyber Defend Africa Academy (courses, quizzes,
assignments, feedback, certificates), instructor and management dashboards,
and a REST API — built with Django, Supabase (PostgreSQL + Storage),
Bootstrap 5, and vanilla JavaScript.

**Tagline:** Defending Today. Securing Tomorrow.

**Repository:** https://github.com/Abdool1500/cyber-defend-africa

## Architecture

```
Browser
  |
  v
Django Templates + Bootstrap 5 + JavaScript
  |
  v
Django (auth, ORM, business logic, role-based authorization, REST API)
  |
  v
Supabase (managed PostgreSQL + Storage)
```

Django Authentication is the single source of truth for identity —
Supabase is used only as a hosted Postgres database and file storage
provider, not as a competing auth system.

## Tech stack

- Python 3.12+, Django 5.1, Django REST Framework, drf-spectacular
- Supabase PostgreSQL (via `psycopg`), Supabase Storage (via `requests`)
- Bootstrap 5, vanilla ES6+ JavaScript, Jest
- ReportLab (PDF reports/certificates), WhiteNoise (static files), Gunicorn

## Local development

```bash
git clone <repo-url>
cd cyber-defend-africa
./scripts/setup.sh
```

Or step by step:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
npm install
cp .env.example .env          # then fill in your Supabase credentials
python manage.py migrate
python manage.py seed_demo_data
python manage.py create_initial_superadmin
python manage.py runserver
```

Without `DATABASE_URL` set, the app falls back to local SQLite so you can
develop before Supabase credentials are available — see
`docs/supabase-setup.md` for connecting to a real project.

## Running tests

```bash
python manage.py test     # Django tests (always run against config.settings.test)
npm test                  # Jest tests for static/js/modules/*
./scripts/test.sh         # everything CI runs, in one command
```

## Project layout

```
config/settings/     split settings: base / development / production / test
apps/                one Django app per domain (accounts, courses, quizzes, ...)
templates/            base.html + public/, accounts/, student/, instructor/, management/
static/css, static/js  brand CSS + JS modules (with static/js/modules/__tests__)
docs/                 Unix workflow + Supabase setup guides
tasks/todo.md         build plan and phase-by-phase status
```

## Key docs

- [`docs/supabase-setup.md`](docs/supabase-setup.md) — connecting to a real
  Supabase project (database + storage)
- [`docs/unix-development.md`](docs/unix-development.md) — shell command
  reference used throughout this workflow
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — branching, commit, and PR conventions
- [`SECURITY.md`](SECURITY.md) — responsible disclosure

## Environment variables

See `.env.example` for the full list. Never commit `.env`.

## Roles

`student` (public self-registration), `instructor`, `admin`, `super_admin`
(created only via `create_initial_superadmin` or promoted through Django
Admin — never selectable at public registration).

## Known limitations

- No live Supabase project is wired up yet — `DATABASE_URL` and the
  `SUPABASE_*` storage credentials are placeholders in `.env`. The app runs
  against local SQLite until they're supplied.
- The custom management dashboard covers platform-wide statistics; use
  Django Admin for full CRUD on individual records (users, courses,
  enrollments, leads, resources, audit logs) until dedicated management
  screens are built out.
- `WAITLIST_FORM_URL` in the committed `.env` points to the Google Form
  provided during setup — replace it if that form is retired.
