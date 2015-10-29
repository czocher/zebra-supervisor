# -*- coding: utf-8 -*-
from django import forms

from django.utils.translation import ugettext_lazy as _

from judge.models import Problem

from .models import Question


class QuestionForm(forms.ModelForm):
    title = forms.CharField(label=_("Title"),
                            widget=forms.TextInput, required=True)
    question = forms.CharField(label=_("Question"),
                               widget=forms.Textarea, required=True)
    contest = None

    def __init__(self, * args, **kwargs):
        contest = kwargs.pop('contest')
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields['problem'] = forms.ModelChoiceField(
            queryset=Problem.objects.filter(contests=contest),
            empty_label=_("General"), required=False)
        self.fields['problem'].label = _("Problem")

    class Meta:
        model = Question
        fields = ('problem', 'title', 'question')

    def clean(self):
        return super(QuestionForm, self).clean()
