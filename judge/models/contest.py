# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Count

from django.conf import settings

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils.six import iterkeys

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

from copy import deepcopy

from .problem import Problem


@python_2_unicode_compatible
class Contest(models.Model):

    """Model representing a single contest."""
    name = models.CharField(_("Name"), max_length=255)
    start_time = models.DateTimeField(_("Start time"), default=timezone.now)
    freeze_time = models.DateTimeField(_("Freeze time"), default=timezone.now)
    end_time = models.DateTimeField(_("End time"), default=timezone.now)
    problems = models.ManyToManyField(
        Problem, verbose_name=_("Problems"), related_name='contests')
    team = models.BooleanField(_("Team contest"), default=False)
    penalty = models.IntegerField(
        _("Penalty for wrong submissions"), default=0)
    printing = models.BooleanField(_("Is printing avaliable"), default=False)

    class Meta:
        verbose_name = _("Contest")
        verbose_name_plural = _("Contests")
        ordering = ['name']
        permissions = (
            ('view_contest', "Can view Contest"),
            ('see_unfrozen_ranking', "Can see unfrozen ranking")
        )
        app_label = 'judge'

    def __str__(self):
        return u"{}".format(self.name)

    def get_absolute_url(self):
        return reverse('contest', args=(self.id, ))

    def _is_active(self):
        return timezone.now() > self.start_time and \
            timezone.now() < self.end_time
    _is_active.boolean = True
    _is_active.short_description = _("Active")
    is_active = property(_is_active)

    def _is_started(self):
        return timezone.now() > self.start_time
    _is_started.boolean = True
    _is_started.short_desctiption = _("Started")
    is_started = property(_is_started)

    def _is_finished(self):
        return timezone.now() > self.end_time
    _is_finished.boolean = True
    _is_finished.short_description = _("Finished")
    is_finished = property(_is_finished)

    def _is_freezed(self):
        return timezone.now() > self.freeze_time and \
            timezone.now() < self.end_time
    _is_freezed.boolean = True
    _is_freezed.short_desctiption = _("Freezed")
    is_freezed = property(_is_freezed)

    def _is_printing_available(self):
        return self.printing \
            and getattr(settings, 'PRINTING_AVAILABLE', False) \
            and self.is_active
    _is_printing_available.boolean = True
    _is_printing_available.short_description = _("Printing")
    is_printing_available = property(_is_printing_available)

    def clean(self):
        if not self.start_time <= self.end_time:
            raise ValidationError({'start_time':
                _("Contest start time can not be after its end time.")})

        if not self.start_time <= self.freeze_time:
            raise ValidationError({'freeze_time':
                _("Contest freeze time can not be before its start time.")})

        if not self.freeze_time <= self.end_time:
            raise ValidationError({'freeze_time':
                _("Contest freeze time can not be after its end time.")})

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Contest, self).save(*args, **kwargs)

    class Res(object):

        def __init__(self):
            self.score = 0
            self.total = 0
            self.timestamp = 0

    def getProblemsAndLastUsersSubmissions(self, includeFreezing):
        # pylint: disable=no-member
        contestSubmissions = self.submissions.judged().values(
            "author", "problem", "problem__codename", "author__pk").annotate(
                Count("id")).order_by("problem__name")

        if includeFreezing:
            contestSubmissions = contestSubmissions.filter(
                timestamp__lte=self.freeze_time)

        problems = {}
        for problem in self.problems.order_by("codename"):
            problems[problem.codename] = self.Res()

        users = {}

        for submission in contestSubmissions:
            if submission["author"] not in users:
                # pylint: disable=no-member
                users[submission["author"]] = User.objects.get(
                    pk=(submission["author__pk"]))
                users[submission["author"]].problems = deepcopy(problems)
                users[submission["author"]].score = 0
                users[submission["author"]].totalTime = 0
                users[submission["author"]].currentSubmissions = []
            totalSubmissions = submission["id__count"]
            # pylint: disable=no-member
            lastSub = self.submissions.order_by("-timestamp").filter(
                author__exact=submission["author"],
                problem__exact=submission["problem"])
            if includeFreezing:
                lastSub = lastSub.filter(timestamp__lte=self.freeze_time)
            lastSub = lastSub[0]
            users[submission["author"]].score += lastSub.score
            users[submission["author"]].problems[
                submission["problem__codename"]].score = lastSub.score
            users[submission["author"]].problems[
                submission["problem__codename"]].total = totalSubmissions
            users[submission["author"]].problems[
                submission["problem__codename"]].timestamp = lastSub.timestamp
            users[submission["author"]].currentSubmissions.append(lastSub)

        return sorted(iterkeys(problems)), users
