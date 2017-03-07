# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView, TemplateView

from django.contrib.admin.views.decorators import staff_member_required

from django.utils.decorators import method_decorator

from django.shortcuts import get_object_or_404

from judge.models import Contest, Submission

from .mixins import ValidRequestMixin


class ContestListView(ListView):

    template_name = 'contest_list.html'
    context_object_name = 'contest_list'
    model = Contest

    def get_context_data(self):
        context = super(ContestListView, self).get_context_data()
        # pylint: disable=no-member
        context['submissions'] = Submission.objects.filter(
            author=self.request.user)
        return context


class ContestDetailView(ValidRequestMixin, DetailView):

    template_name = 'contest_detail.html'
    context_object_name = 'contest'
    pk_url_kwarg = 'contest_pk'
    model = Contest


class ContestSubmissionListView(ListView):

    template_name = 'contest_submission_list.html'
    context_object_name = 'submission_list'
    model = Submission
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super(
            ContestSubmissionListView, self).get_context_data(**kwargs)
        context['contest'] = get_object_or_404(
            Contest, pk=self.kwargs['contest_pk'])
        return context

    def get_queryset(self):
        submissions = super(ContestSubmissionListView, self).get_queryset()
        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])
        submissions = submissions.filter(
            author=self.request.user, contest=contest)
        return submissions


@method_decorator(staff_member_required, name='dispatch')
class LatestContestSubmissionsTemplateView(ValidRequestMixin, DetailView):

    template_name = 'latest_contest_submissions.html'
    context_object_name = 'contest'
    pk_url_kwarg = 'contest_pk'
    model = Contest

    def get_context_data(self, **kwargs):
        context = super(
            LatestContestSubmissionsTemplateView, self).get_context_data(
                **kwargs)
        contest = self.get_object()
        submissions = contest.submissions.all()[:8]
        context['submissions'] = submissions
        return context
