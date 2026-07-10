.PHONY: install migrate seed run test test-js check collectstatic superuser

install:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements-dev.txt
	npm install

migrate:
	.venv/bin/python manage.py migrate

seed:
	.venv/bin/python manage.py seed_demo_data

run:
	.venv/bin/python manage.py runserver

test:
	.venv/bin/python manage.py test

test-js:
	npm test

check:
	.venv/bin/python manage.py check
	.venv/bin/python manage.py makemigrations --check --dry-run

collectstatic:
	.venv/bin/python manage.py collectstatic --noinput

superuser:
	.venv/bin/python manage.py create_initial_superadmin
