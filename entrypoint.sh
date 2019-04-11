#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

cp zebra/docker.py zebra/settings.py
python manage.py flush --no-input
python manage.py migrate
python manage.py collectstatic --no-input
gunicorn zebra.wsgi:application --bind 0.0.0.0:8000
