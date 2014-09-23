from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
import datetime
from django.conf import settings

import uuid


class Language(models.Model):
    """Available node language class."""
    name = models.CharField(_("Name"), max_length=50)
    name.help_text = _("Example: C++")
    compiler = models.CharField(_("Compiler command"), max_length=255)
    compiler.help_text = _("Example: g++")
    arguments = models.CharField(_("Compiler arguments"), max_length=255)
    arguments.help_text = _("Example: -Wall -Wextra -pedantic -oresult")
    filename = models.CharField(_("Result filename"), max_length=255)
    filename.help_text = _("Example: result")

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")

    def __unicode__(self):
        return u"%s" % (self.name, )


class Node(models.Model):
    """Class representing the system node used for solution testing."""
    name = models.CharField(_("Name"), max_length=255)
    key = models.CharField(_("Key"), max_length=255)
    authorized = models.BooleanField(_("Authorized"), default=False)

    class Meta:
        verbose_name = _("Node")
        verbose_name_plural = _("Nodes")

    def __unicode__(self):
        return u"%s" % (self.name, )


class NodeInfo(models.Model):
    """Node hardware and software information."""
    ip = models.IPAddressField(_("IP Address"), blank=True, null=True)
    version = models.CharField(_("Version"), max_length=255, blank=True, null=True)
    memory = models.CharField(_("Free memory"), max_length=255,  blank=True, null=True)
    disk = models.CharField(_("Disk space"), max_length=255, blank=True, null=True)
    frequency = models.CharField(_("Processor frequency"), max_length=255,  blank=True, null=True)
    languages = models.ManyToManyField(Language, verbose_name=_("Supported languages"), related_name='languages', blank=True, null=True)
    node = models.OneToOneField(Node, verbose_name=_("Node"), related_name="info")

    class Meta:
        verbose_name = _("Node information")
        verbose_name_plural = _("Node informations")

    def __unicode__(self):
        return u"%s (%s)" % (self.ip, self.version)


REST_SESSION_DURATION = getattr(settings, 'REST_SESSION_DURATION', 900)


class NodeSession(models.Model):
    id = models.CharField(_("ID"), primary_key=True, max_length=36, default=uuid.uuid1, editable=False)
    node = models.ForeignKey(Node, verbose_name=_("Node"), related_name='node_session')
    expiration_time = models.DateTimeField(_("Expiration time"),
      default=lambda: timezone.now() + datetime.timedelta(seconds=REST_SESSION_DURATION))
    active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Session")
        verbose_name_plural = _("Sessions")
        ordering = ['expiration_time', ]

    def __unicode__(self):
        return u"%s" % (self.id, )

    def _is_expired(self):
        return timezone.now() > self.expiration_time
    _is_expired.boolean = True
    _is_expired.short_description = _("Expired")
    is_expired = property(_is_expired)
