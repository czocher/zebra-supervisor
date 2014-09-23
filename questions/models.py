from django.db import models

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from judge.models import Contest, Problem


class Question(models.Model):
    author = models.ForeignKey(User, verbose_name=_("Author"), related_name='questions')
    contest = models.ForeignKey(Contest, verbose_name=_("Contest"), related_name='questions')
    problem = models.ForeignKey(Problem, verbose_name=_("Problem"), related_name='questions', blank=True, null=True)
    title = models.CharField(_("Title"), max_length=100)
    question = models.TextField(_("Question"))
    answer = models.TextField(_("Answer"), blank=True, null=True)
    timestamp = models.DateTimeField(_("Send time"), default=timezone.now)
    public = models.BooleanField(_("Public"), default=False)
    readBy = models.ManyToManyField(User, verbose_name=_("Author"))

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ['-timestamp']

    def _is_answered(self):
        if self.answer:
            return True
        return False
    _is_answered.boolean = True
    _is_answered.short_description = _("Answered")
    is_answered = property(_is_answered)

    def __unicode__(self):
        return "%s question from %s" % (self.question, self.author.username)
