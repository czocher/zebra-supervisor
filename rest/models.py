from django.db import models
from django.utils.translation import ugettext_lazy as _


class Node(models.Model):

    """Class representing the system node used for solution testing."""
    ip = models.IPAddressField(_("IP Address"), blank=True, null=True)
    token = models.CharField(_("Token"), max_length=255)
    authorized = models.BooleanField(_("Authorized"), default=False)

    class Meta:
        verbose_name = _("Node")
        verbose_name_plural = _("Nodes")

    def __unicode__(self):
        return u"%s %s" % (self.ip, self.token)
