# -*- coding: utf-8 -*-
from django.db import models

from django.conf import settings

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from django.contrib.auth.models import User

from .contest import Contest
from .problem import Problem


@python_2_unicode_compatible
class PrintRequest(models.Model):

    """Class representing a single print request from a user."""

    WAITING_STATUS = 1
    PRINTING_STATUS = 2
    PRINTED_STATUS = 3

    STATUS_CHOICES = (
        (WAITING_STATUS, _("Waiting")),
        (PRINTING_STATUS, _("Printing")),
        (PRINTED_STATUS, _("Printed")),
    )

    PRINTING_LANGUAGES = list(settings.PROGRAMMING_LANGUAGES)
    PRINTING_LANGUAGES.extend((('plain', 'Plain'), ))

    status = models.IntegerField(
        _("Status"), choices=STATUS_CHOICES, default=WAITING_STATUS)
    author = models.ForeignKey(
        User, verbose_name=_("Author"), related_name='printRequests')
    source = models.TextField(_("Source code"))
    timestamp = models.DateTimeField(_("Send time"), default=timezone.now)
    language = models.CharField(
        _("Language"), max_length=10, choices=PRINTING_LANGUAGES)
    contest = models.ForeignKey(Contest, verbose_name=_(
        "Contest"), related_name='printRequests', blank=True, null=True)
    problem = models.ForeignKey(
        Problem, verbose_name=_("Problem"), related_name='printRequests',
        blank=True, null=True)

    class Meta:
        verbose_name = _("Print request")
        verbose_name_plural = _("Print requests")
        ordering = ['-timestamp']
        app_label = 'judge'

    def __str__(self):
        return u"Print request by {} for {} in {}".format(
            self.author.username, self.problem, self.contest)

    def get_status_codename(self):
        if self.status == self.WAITING_STATUS:
            return 'Waiting'
        elif self.status == self.PRINTING_STATUS:
            return 'Printing'
        else:
            return 'Printed'
