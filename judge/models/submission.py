# -*- coding: utf-8 -*-
from django.db import models

from django.conf import settings

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

from pygments import highlight
from pygments.lexers import get_lexer_by_name
# pylint: disable=no-name-in-module
from pygments.formatters import HtmlFormatter

from rest.models import Node

from .problem import Problem
from .contest import Contest


class SubmissionManager(models.Manager):

    def judged(self):
        return super(SubmissionManager, self).get_queryset().filter(
            status=Submission.JUDGED_STATUS)

    def judging(self):
        return super(SubmissionManager, self).get_queryset().filter(
            status=Submission.JUDGING_STATUS)

    def waiting(self):
        return super(SubmissionManager, self).get_queryset().filter(
            status=Submission.WAITING_STATUS)


class Submission(models.Model):

    """Class representing a single user submited solution for a problem."""

    WAITING_STATUS = 1
    JUDGING_STATUS = 2
    JUDGED_STATUS = 3

    STATUS_CHOICES = (
        (WAITING_STATUS, _("Waiting")),
        (JUDGING_STATUS, _("Judging")),
        (JUDGED_STATUS, _("Judged")),
    )

    author = models.ForeignKey(
        User, verbose_name=_("Author"), related_name='submissions')
    problem = models.ForeignKey(
        Problem, verbose_name=_("Problem"), related_name='submissions')
    contest = models.ForeignKey(Contest, verbose_name=_(
        "Contest"), related_name='submissions', blank=True, null=True)
    source = models.TextField(_("Source code"))
    language = models.CharField(
        _("Language"), max_length=10, choices=settings.PROGRAMMING_LANGUAGES)
    timestamp = models.DateTimeField(_("Send time"), default=timezone.now)
    compilelog = models.TextField(
        _("Compilation log"), default='', blank=True, null=True)
    score = models.IntegerField(_("Score"), default=(-1))
    status = models.IntegerField(
        _("Status"), choices=STATUS_CHOICES, default=WAITING_STATUS)
    node = models.ForeignKey(Node, verbose_name=_(
        "Node"), blank=True, null=True, on_delete=models.SET_NULL)

    objects = SubmissionManager()

    class Meta:
        verbose_name = _("Submission")
        verbose_name_plural = _("Submissions")
        ordering = ['-timestamp']
        app_label = 'judge'

    def __unicode__(self):
        return u"Solution for {} by {}".format(self.problem.codename,
                                               self.author.username, )

    def get_absolute_url(self):
        return reverse('submission', args=(self.id, ))

    def remove_results(self):
        # pylint: disable=no-member
        for result in self.results.all():
            result.delete()

    @property
    def highlighted_source(self):
        lexer = get_lexer_by_name(self.language, stripall=True)
        formatter = HtmlFormatter(linenos=True)
        return highlight(self.source, lexer, formatter)

    def get_status_codename(self):
        if self.status == self.WAITING_STATUS:
            return 'Waiting'
        elif self.status == self.JUDGING_STATUS:
            return 'Judging'
        else:
            return 'Judged'


class Result(models.Model):

    """Class representing a single test result for a submission."""

    submission = models.ForeignKey(
        Submission, verbose_name=_("Submission"), related_name='results')
    returncode = models.IntegerField(_("Return code"), default=0)
    mark = models.BooleanField(_("Mark"), default=True)
    time = models.FloatField(_("Execution time"), default=0)

    class Meta:
        verbose_name = _("Result")
        verbose_name_plural = _("Results")
        ordering = ['time']
        app_label = 'judge'

    def __unicode__(self):
        return u"{} result for {}".format(self.submission.author.username,
                                          self.submission.problem.codename)
