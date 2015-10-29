# -*- coding: utf-8 -*-
"""This module contains django app utils for the rest app."""
from django.utils.translation import ugettext_lazy as _

from django.apps import AppConfig


class RESTConfig(AppConfig):

    """Config class used for app name and its translation."""

    name = 'rest'
    verbose_name = _("REST")
