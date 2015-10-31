from django.db import models

from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse


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
    pdf = models.FileField(_("PDF"), upload_to='problems/',
                           blank=True, null=True)

    class Meta:
        verbose_name = _("Problem")
        verbose_name_plural = _("Problems")
        ordering = ['codename', ]
        app_label = 'judge'

    def __unicode__(self):
        return u"{} ({})".format(self.name, self.codename)

    def get_absolute_url(self):
        return reverse('problem', args=(self.id, self.codename))

    def _has_pdf(self):
        return bool(self.pdf)
    _has_pdf.boolean = True
    _has_pdf.short_description = _("Has PDF")
    has_pdf = property(_has_pdf)


class SampleIO(models.Model):
    input = models.TextField(_("Input"))
    output = models.TextField(_("Output"))
    problem = models.ForeignKey(Problem, verbose_name=_("Problem"))

    class Meta:
        verbose_name = _("Sample I/O")
        verbose_name_plural = _("Sample I/O")
        app_label = 'judge'

    def __unicode__(self):
        return u"{}".format(self.id)
