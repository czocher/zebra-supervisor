# -*- coding: utf-8 -*-
"""This module contains django app utils for the judge app."""
from django.utils.translation import ugettext_lazy as _
from django.apps import AppConfig


class JudgeConfig(AppConfig):

    """Config class used for app name and its translation."""

    name = 'judge'
    verbose_name = _("Judge")
