# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Count

from django.conf import settings

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

from rest.models import Node
from copy import deepcopy

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


class Problem(models.Model):

    """Model representing a single problem."""

    EXAMPLE_PROBLEM = """
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Curabitur id tortor at dui porta sollicitudin in sit amet nisi.
Nunc venenatis tincidunt orci eget imperdiet.
Maecenas rutrum arcu at nunc aliquet pulvinar.
Maecenas blandit augue nec augue semper id ornare lorem congue.
Etiam non erat lorem, eget semper eros.</p>

<h3>Input</h3>
On the input the program recives two binary numbers.

<h3>Output</h3>
On the output the program should print a binary number.
"""

    codename = models.SlugField(_("Codename"), max_length=10, unique=True)
    codename.help_text = _(
        "Example: 'FIB01'. "
        "A short text to identify this problem, used as an id for urls."
    )
    name = models.CharField(_("Name"), max_length=255)
    content = models.TextField(_("Content"), default=EXAMPLE_PROBLEM)

    class Meta:
        verbose_name = _("Problem")
        verbose_name_plural = _("Problems")
        ordering = ['codename',]

    def __unicode__(self):
        return u"{} ({})".format(self.name, self.codename)

    def get_absolute_url(self):
        return reverse('problem', args=(self.id, self.codename))


class SampleIO(models.Model):
    input = models.TextField(_("Input"))
    output = models.TextField(_("Output"))
    problem = models.ForeignKey(Problem, verbose_name=_("Problem"))

    class Meta:
        verbose_name = _("Sample I/O")
        verbose_name_plural = _("Sample I/O")

    def __unicode__(self):
        return u"{}".format(self.id)


class Test(models.Model):
    timestamp = models.DateTimeField(_("Timestamp"), default=timezone.now)
    file = models.FileField(_("Tests File"), upload_to='tests/')

    class Meta:
        abstract = True
        ordering = ['timestamp']

    def __unicode__(self):
        return u"{}".format(self.name,)

    @property
    def name(self):
        return self.file.name[6:]


class InputTest(Test):

    class Meta:
        verbose_name = _("Test input")
        verbose_name_plural = _("Test inputs")

    @property
    def problem(self):
        return self.input.problem.codename


class OutputTest(Test):

    class Meta:
        verbose_name = _("Test output")
        verbose_name_plural = _("Test outputs")

    @property
    def problem(self):
        return self.output.problem.codename


class ConfigTest(Test):

    class Meta:
        verbose_name = _("Test config")
        verbose_name_plural = _("Test configs")

    @property
    def problem(self):
        return self.config.problem.codename


class Tests(models.Model):
    input = models.OneToOneField(
        InputTest, verbose_name=_("Inputs"), related_name='input')
    output = models.OneToOneField(
        OutputTest, verbose_name=_("Outputs"), related_name='output')
    config = models.OneToOneField(
        ConfigTest, verbose_name=_("Config"), related_name='config')
    problem = models.OneToOneField(Problem, verbose_name=_("Problem"))

    class Meta:
        verbose_name = _("Tests")
        verbose_name_plural = _("Tests")

    def __unicode__(self):
        return u"Tests for {}".format(self.problem.codename,)


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

    def __unicode__(self):
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

    class Res(object):

        def __init__(self):
            self.score = 0
            self.total = 0
            self.timestamp = 0

    def getProblemsAndLastUsersSubmissions(self, includeFreezing):
        contestSubmissions = Submission.objects.filter(
            status=Submission.JUDGED_STATUS, contest=self).values(
                "author", "problem",
                "problem__codename", "author__pk").annotate(
                    Count("id")).order_by("problem__name")

        if (includeFreezing):
            contestSubmissions = contestSubmissions.filter(
                timestamp__lte=self.freeze_time)

        problems = {}
        for problem in self.problems.order_by("codename"):
            problems[problem.codename] = self.Res()

        users = {}

        for submission in contestSubmissions:
            if submission["author"] not in users:
                users[submission["author"]] = User.objects.get(
                    pk=(submission["author__pk"]))
                users[submission["author"]].problems = deepcopy(problems)
                users[submission["author"]].score = 0
                users[submission["author"]].totalTime = 0
                users[submission["author"]].currentSubmissions = []
            totalSubmissions = submission["id__count"]
            lastSub = Submission.objects.order_by("-timestamp").filter(
                contest=self, author__exact=submission["author"],
                problem__exact=submission["problem"])
            if (includeFreezing):
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

        return sorted(problems.iterkeys()), users


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

    class Meta:
        verbose_name = _("Submission")
        verbose_name_plural = _("Submissions")
        ordering = ['-timestamp']

    def __unicode__(self):
        return u"Solution for {} by {}".format(self.problem.codename,
                                          self.author.username, )

    def get_absolute_url(self):
        return reverse('submission', args=(self.id, ))

    def remove_results(self):
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

    def __unicode__(self):
        return u"{} result for {}".format(self.submission.author.username,
                                     self.submission.problem.codename)


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

    def __unicode__(self):
        return u"Print request by {} for {} in {}".format(
            self.author.username, self.problem, self.contest)

    def get_status_codename(self):
        if self.status == self.WAITING_STATUS:
            return 'Waiting'
        elif self.status == self.PRINTING_STATUS:
            return 'Printing'
        else:
            return 'Printed'
