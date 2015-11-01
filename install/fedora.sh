#!/bin/bash

if [ "$PWD" != "/var/www/zebra-supervisor/install" ]; then
  echo "Move zebra-supervisor to /var/www/ then rerun this script."
else
  sudo pip install -r ../requirements.txt
  sudo dnf install httpd mod_wsgi
  sudo cp ../zebra/default_settings.py ../zebra/settings.py
  sudo cp ./zebra.conf /etc/httpd/conf.d/
  sudo ../manage.py collectstatic
  sudo ../manage.py compilemessages
  sudo ../manage.py makemigrations
  sudo ../manage.py migrate
  sudo chown apache:apache -R ../*
  sudo systemctl restart httpd
fi
