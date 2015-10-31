# -*- coding: utf-8 -*-
from django.views.generic import DetailView
from django.views.generic.base import View

from django.http import Http404

from sendfile import sendfile

from judge.models import Problem

from .mixins import ValidRequestMixin


class ProblemDetailView(ValidRequestMixin, DetailView):

    template_name = 'problem_detail.html'
    context_object_name = 'problem'
    model = Problem
    slug_field = 'codename'

    def get_context_data(self, **kwargs):
        context = super(ProblemDetailView, self).get_context_data(**kwargs)
        context['contest'] = self.contest
        return context


class ProblemPDFView(ValidRequestMixin, View):

    """Return a PDF file attached to the given problem if it exists."""

    def get(self, request, *args, **kwargs):
        if not self.problem.pdf:
            raise Http404

        return sendfile(request, self.problem.pdf.path)
