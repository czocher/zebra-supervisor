#!/bin/bash

echo "Remember to change the database and DEBUG settings!"
cp ../zebra/default_settings.py ../zebra/settings.py
pip install -r ../requirements.txt
../manage.py compilemessages
../manage.py makemigrations
../manage.py migrate

