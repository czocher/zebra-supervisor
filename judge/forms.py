# -*- coding: utf-8 -*-
"""This module contains forms used in the judge app."""
from django import forms

from django.utils.translation import ugettext_lazy as _
from judge.models import Submission, PrintRequest


class SubmissionForm(forms.ModelForm):

    """Submission creation form class."""

    source = forms.CharField(label=_("Source code"),
                             widget=forms.Textarea, required=False)
    sourcefile = forms.FileField(label=_("Source file"), required=False)

    class Meta:
        model = Submission
        fields = ('language', 'source')

    def clean(self):
        sourcefile = self.cleaned_data.get('sourcefile')
        sourcecode = self.cleaned_data.get('source')

        if len(sourcecode) == 0 and not sourcefile:
            raise forms.ValidationError(_("Please provide code to submit."))
        elif len(sourcecode) == 0 and sourcefile.size > 100000:
            raise forms.ValidationError(_("File is too large for submission."))
        elif len(sourcecode) == 0 and sourcefile:
            if not sourcefile.content_type.startswith('text'):
                raise forms.ValidationError(_("Cannot submit binary file."))
            else:
                self.cleaned_data['source'] = sourcefile.read()

        return super(SubmissionForm, self).clean()


class PrintRequestForm(forms.ModelForm):

    """Print request creation form class."""

    source = forms.CharField(label=_("Content"),
                             widget=forms.Textarea, required=False)
    sourcefile = forms.FileField(label=_("Content file"), required=False)

    class Meta:
        model = PrintRequest
        fields = ('language', 'source')

    def clean(self):
        sourcefile = self.cleaned_data.get('sourcefile')
        sourcecode = self.cleaned_data.get('source')

        if len(sourcecode) == 0 and not sourcefile:
            raise forms.ValidationError(
                _("Please provide content for printing."))
        elif len(sourcecode) == 0 and sourcefile.size > 100000:
            raise forms.ValidationError(_("File is too large for submission."))
        elif len(sourcecode) == 0 and sourcefile:
            if not sourcefile.content_type.startswith('text'):
                raise forms.ValidationError(_("Cannot submit binary file."))
            else:
                self.cleaned_data['source'] = sourcefile.read()

        return super(PrintRequestForm, self).clean()
