#!/bin/bash

if [ "$PWD" != "/var/www/zebra-supervisor/install" ]; then
  echo "Move zebra-supervisor to /var/www/ then rerun this script."
else
  sudo pip install -r ../requirements.txt
  sudo dnf install httpd mod_wsgi mod_xsendfile MySQL-python
  sudo cp ../zebra/production.py ../zebra/settings.py
  sudo cp ./zebra.conf /etc/httpd/conf.d/
  sudo ../manage.py collectstatic
  sudo ../manage.py compilemessages
  sudo chown apache:apache -R ../*
  sudo systemctl enable httpd
  sudo systemctl restart httpd
  sudo systemctl enable mariadb
  sudo systemctl restart mariadb
  sudo mysql_secure_installation
  echo "Please enter the MySQL root password to create a database"
  mysql -uroot -p -e "CREATE DATABASE zebra CHARACTER SET utf8"
  echo "Change settings.py MySQL password!"
  read -p "Press any key to continue... " -n1 -s
  sudo ../manage.py makemigrations
  sudo ../manage.py migrate
  echo "If above failed it's because settings.py has the wrong password"
  sudo chown apache:apache -R ../*
  echo "Remember to disable SELinux"
fi
