#!/bin/sh
rm -rf api/migrations/00*
rm -rf landing/migrations/00*
rm -rf support/migrations/00*
sleep 10
python manage.py makemigrations
python manage.py migrate_schemas
python manage.py collectstatic --noinput
python manage.py loaddata data.json
gunicorn app.wsgi:application -w 1 -b 0.0.0.0:8000 --log-level=debug -e ENV=prod