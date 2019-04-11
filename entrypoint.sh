#!/bin/sh

if [ -z "$SECRET_KEY" ]; then
  EXAMPLE_SECRET_KEY=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1`
  echo "!!!!! Set SECRET_KEY to a random value !!!!!\n
For example: $EXAMPLE_SECRET_KEY, generated with: 'cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1'"
  exit 1
fi

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.5
    done

    echo "PostgreSQL started"
fi

python manage.py flush --no-input
python manage.py migrate
python manage.py collectstatic --no-input
gunicorn zebra.wsgi:application --bind 0.0.0.0:8000
