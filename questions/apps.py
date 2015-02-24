# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.apps import AppConfig


class QuestionsConfig(AppConfig):
        name = 'questions'
        verbose_name = _("Questions")
