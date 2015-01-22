from django.utils.translation import ugettext_lazy as _
from django.apps import AppConfig


class RESTConfig(AppConfig):
        name = 'rest'
        verbose_name = _("REST")
