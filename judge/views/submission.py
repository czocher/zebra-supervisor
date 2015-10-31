# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.base import View

from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.contrib.messages.api import success, error

from judge.models import Submission, PrintRequest
from judge.forms import SubmissionForm, PrintRequestForm

from .mixins import ValidRequestMixin


class SubmissionCreateView(ValidRequestMixin, CreateView):

    template_name = 'submission_form.html'
    model = Submission
    form_class = SubmissionForm
    success_url = '../../../submissions/'

    def dispatch(self, request, *args, **kwargs):

        if not self.contest.is_active and not request.user.is_superuser:
            raise PermissionDenied

        return super(SubmissionCreateView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SubmissionCreateView, self).get_context_data(**kwargs)

        context['problem'] = self.problem
        context['contest'] = self.contest
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.problem = self.problem
        form.instance.contest = self.contest
        return super(SubmissionCreateView, self).form_valid(form)


class SubmissionListView(ListView):

    template_name = 'submission_list.html'
    context_object_name = 'submission_list'
    model = Submission
    allow_empty = True

    def get_queryset(self):
        submissions = super(SubmissionListView, self).get_queryset()
        submissions = submissions.filter(author=self.request.user)
        return submissions


class SubmissionDetailView(DetailView):

    template_name = 'submission_detail.html'
    context_object_name = 'submission'
    model = Submission

    def get_object(self, queryset=None):
        submission = super(SubmissionDetailView, self).get_object()

        if submission.author != self.request.user:
            raise PermissionDenied
        else:
            return submission


class SubmissionPrintView(View):

    def get(self, request, *args, **kwargs):
        submission = get_object_or_404(Submission, pk=self.kwargs['pk'])
        if not submission.contest.is_printing_available or \
           submission.author != self.request.user:
            error(request, _("Printing not available."))
        else:
            print_request = PrintRequest(
                source=submission.source,
                language=submission.language,
                contest=submission.contest,
                author=submission.author,
                problem=submission.problem)
            print_request.save()
            success(request, _("Print request added to print queue."))

        return redirect('submission', int(self.kwargs['pk']))


class SubmissionPrintCreateView(ValidRequestMixin, FormView):

    model = PrintRequest
    form_class = PrintRequestForm
    template_name = 'print_submission_form.html'
    success_url = '../'

    def get_context_data(self, **kwargs):
        context = super(
            SubmissionPrintCreateView, self).get_context_data(**kwargs)

        if not self.contest.is_printing_available:
            raise PermissionDenied

        context['contest'] = self.contest
        return context

    def form_valid(self, form):
        if not self.contest.is_printing_available:
            raise PermissionDenied

        print_request = PrintRequest(
            source=form.cleaned_data['source'],
            language=form.cleaned_data['language'],
            contest=self.contest,
            author=self.request.user)
        print_request.save()

        success(self.request, _("Print request added to print queue."))
        return super(SubmissionPrintCreateView, self).form_valid(form)
