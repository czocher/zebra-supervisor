# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import pre_delete

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from .problem import Problem


@python_2_unicode_compatible
class Test(models.Model):
    timestamp = models.DateTimeField(_("Timestamp"), default=timezone.now)
    file = models.FileField(_("Tests File"), upload_to='tests/')

    class Meta:
        abstract = True
        ordering = ['timestamp']
        app_label = 'judge'

    def __str__(self):
        return u"{}".format(self.name,)

    @property
    def name(self):
        return self.file.name[6:]


class InputTest(Test):

    class Meta:
        verbose_name = _("Test input")
        verbose_name_plural = _("Test inputs")
        app_label = 'judge'

    @property
    def problem(self):
        # pylint: disable=no-member
        return self.input.problem.codename


class OutputTest(Test):

    class Meta:
        verbose_name = _("Test output")
        verbose_name_plural = _("Test outputs")
        app_label = 'judge'

    @property
    def problem(self):
        # pylint: disable=no-member
        return self.output.problem.codename


class ConfigTest(Test):

    class Meta:
        verbose_name = _("Test config")
        verbose_name_plural = _("Test configs")
        app_label = 'judge'

    @property
    def problem(self):
        # pylint: disable=no-member
        return self.config.problem.codename


def remove_test_file(sender, instance, **kwargs):
    """Remove test files on Test model deletion."""
    instance.file.delete(False)
pre_delete.connect(remove_test_file, sender=InputTest)
pre_delete.connect(remove_test_file, sender=OutputTest)
pre_delete.connect(remove_test_file, sender=ConfigTest)


@python_2_unicode_compatible
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
        app_label = 'judge'

    def __str__(self):
        return u"Tests for {}".format(self.problem.codename,)
