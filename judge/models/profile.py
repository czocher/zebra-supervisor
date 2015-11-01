# -*- coding: utf-8 -*-

"""Module containing judge user profiles and various utilities."""

from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Profile(models.Model):

    """The users profile class."""

    user = models.OneToOneField(User, related_name='profile')
    institute_name = models.CharField(_("Institute name"), max_length=255,
                                      blank=True, null=True)
    team_name = models.CharField(_("Team name"), max_length=255, blank=True,
                                 null=True)
    room_number = models.CharField(_("Room number"), max_length=10, blank=True,
                                   null=True)
    computer_number = models.CharField(_("Computer number"), max_length=10,
                                       blank=True, null=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        app_label = 'judge'

    def __unicode__(self):
        return u"{}".format(self.user.username)


def create_profile(sender, instance, created, **kwargs):
    """Create an empty profile as soon as a user is created."""
    if created:
        Profile.objects.create(user=instance)
post_save.connect(create_profile, sender=User)
