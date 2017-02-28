# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core import serializers
from django.conf import settings
import os


FIXTURE_DIR = getattr(settings, 'FIXTURE_DIR', os.path.dirname(__file__))


def get_fixture_file_paths():
    fixture_file_paths = []

    for name in os.listdir(FIXTURE_DIR):
        path = os.path.join(FIXTURE_DIR, name)
        if os.path.isfile(path) and path.endswith(('xml', 'json', 'yaml')):
            fixture_file_paths.append(path)

    return fixture_file_paths


def initial_data(apps, schema_editor):

    for filepath in get_fixture_file_paths():

        with open(filepath, 'r') as fixtures:
            objects = serializers.deserialize(
                os.path.splitext(filepath)[1][1:],
                fixtures, ignorenonexistent=True)

            for obj in objects:
                obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0001_initial'),
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_data),
    ]
