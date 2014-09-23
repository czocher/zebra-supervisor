from django import forms

from django.utils.translation import ugettext_lazy as _
from judge.models import Submission

class SubmissionForm(forms.ModelForm):
    source = forms.CharField(label=_("Source code"), widget=forms.Textarea, required=False)
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
            self.cleaned_data['source'] = self.cleaned_data['sourcefile'].read()

        return super(SubmissionForm, self).clean()
