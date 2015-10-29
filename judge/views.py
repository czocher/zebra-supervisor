# -*- coding: utf-8 -*-
# pylint: disable=too-many-ancestors
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.base import View

from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.contrib.messages.api import success, error

from datetime import timedelta
from collections import OrderedDict
from sendfile import sendfile

from .models import Contest, Problem, Submission, PrintRequest
from .forms import SubmissionForm, PrintRequestForm


class ValidRequestMixin(object):

    """Check if user has the permissions to view
    the given contest or problem."""

    @property
    def contest(self):
        return get_object_or_404(Contest, pk=self.kwargs['contest_pk'])

    @property
    def problem(self):
        codename = self.kwargs.get('slug', None)
        if codename is not None:
            return get_object_or_404(Problem, codename=codename)
        return None

    def _check_contest_permissions(self):
        """Check if the user can view the given contest."""
        user = self.request.user
        if not user.has_perm('view_contest', self.contest):
            raise PermissionDenied
        elif not self.contest.is_started and not user.is_superuser:
            raise PermissionDenied

    def _check_problem_exists(self):
        """Check if problem exists in the given contest."""
        if self.problem is not None \
                and self.problem not in self.contest.problems.all():
            raise Http404

    def dispatch(self, request, *args, **kwargs):

        self._check_contest_permissions()

        self._check_problem_exists()

        return super(ValidRequestMixin, self).dispatch(
            request, *args, **kwargs)


class ContestListView(ListView):

    template_name = 'contest_list.html'
    context_object_name = 'contest_list'
    model = Contest

    def get_context_data(self):
        context = super(ContestListView, self).get_context_data()
        context['submissions'] = Submission.objects.filter(
            author=self.request.user)
        return context


class ContestDetailView(ValidRequestMixin, DetailView):

    template_name = 'contest_detail.html'
    context_object_name = 'contest'
    pk_url_kwarg = 'contest_pk'
    model = Contest


class ProblemDetailView(ValidRequestMixin, DetailView):

    template_name = 'problem_detail.html'
    context_object_name = 'problem'
    model = Problem
    slug_field = 'codename'

    def get_context_data(self, **kwargs):
        context = super(ProblemDetailView, self).get_context_data(**kwargs)
        context['contest'] = self.contest
        return context


class SubmissionCreateView(ValidRequestMixin, CreateView):

    template_name = 'submission_form.html'
    model = Submission
    form_class = SubmissionForm
    success_url = '../../../submissions/'

    def dispatch(self, request, *args, **kwargs):

        if not self.contest.is_active:
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


class ScoreRankingListView(ValidRequestMixin, TemplateView):

    template_name = 'ranking_list.html'
    context_object_name = 'ranking_list'

    def get_context_data(self, **kwargs):
        context = super(ScoreRankingListView, self).get_context_data(**kwargs)

        include_freezed = True
        user = self.request.user
        if user.is_superuser or \
                user.has_perm('see_unfrozen_ranking', self.contest):
            include_freezed = False

        problems, users = self.contest.getProblemsAndLastUsersSubmissions(
            include_freezed)

        if len(users) == 0:
            return dict({'empty': True, 'contest': self.contest})

        context['problem_list'] = problems
        context['ranking_list'] = users
        context['contest'] = self.contest

        if self.contest.team:
            self.template_name = 'ranking_time_list.html'
            begin_time = self.contest.start_time
            for dummy, user in context['ranking_list'].items():
                user.score = 0
                user.totalTime = timedelta()
                for dummy, problem in user.problems.items():
                    if problem.score < 100:
                        problem.score = 0
                        problem.timestamp = "-"
                    else:
                        problem.timestamp = problem.timestamp \
                            - begin_time \
                            + timedelta(
                                minutes=(
                                    (problem.total - 1) * self.contest.penalty))
                        user.score += 1
                        user.totalTime += problem.timestamp

        context['ranking_list'] = OrderedDict(
            sorted(users.items(), key=lambda t: (-t[1].score, t[1].totalTime)))

        return context


class ProblemPDFView(ValidRequestMixin, View):

    """Return a PDF file attached to the given problem if it exists."""

    def get(self, request, *args, **kwargs):
        if not self.problem.pdf:
            raise Http404

        return sendfile(request, self.problem.pdf.path)
