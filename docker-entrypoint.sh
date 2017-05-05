#!/bin/sh
rm -rf api/migrations/00*
rm -rf landing/migrations/00*
rm -rf support/migrations/00*
sleep 10
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn app.wsgi:application -w 1 -b 0.0.0.0:8000 --log-level=debug -e ENV=staging