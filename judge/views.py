# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.base import View

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat

from django.template.response import TemplateResponse

from django.utils.html import strip_tags

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.contrib.messages.api import success, error

from datetime import timedelta
from collections import OrderedDict
from judge.models import Contest, Problem, Submission, PrintRequest
from judge.forms import SubmissionForm, PrintRequestForm

from django.http import HttpResponse

import StringIO
from cgi import escape
from xhtml2pdf import pisa


class ContestListView(ListView):

    template_name = 'contest_list.html'
    context_object_name = 'contest_list'
    model = Contest

    def get_context_data(self):
        context = super(ContestListView, self).get_context_data()
        context['submissions'] = Submission.objects.filter(
            author=self.request.user)
        return context


class ContestDetailView(DetailView):

    template_name = 'contest_detail.html'
    context_object_name = 'contest'
    model = Contest

    def get_object(self):
        contest = super(ContestDetailView, self).get_object()
        user = self.request.user

        if not user.has_perm('view_contest', contest):
            raise PermissionDenied
        else:
            return contest


class ProblemDetailView(DetailView):

    template_name = 'problem_detail.html'
    context_object_name = 'problem'
    model = Problem
    slug_field = 'codename'

    def get_object(self):
        problem = super(ProblemDetailView, self).get_object()
        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])

        if problem not in contest.problems.all():
            raise Http404

        user = self.request.user
        if not user.has_perm('view_contest', contest):
            raise PermissionDenied
        elif not contest.is_started and not user.is_superuser:
            raise Http404
        else:
            return problem

    def get_context_data(self, **kwargs):
        context = super(ProblemDetailView, self).get_context_data(**kwargs)
        context['contest'] = get_object_or_404(
            Contest, pk=self.kwargs['contest_pk'])
        return context


class SubmissionCreateView(CreateView):

    template_name = 'submission_form.html'
    model = Submission
    form_class = SubmissionForm
    success_url = '../../../submissions/'

    def get_context_data(self, **kwargs):
        context = super(SubmissionCreateView, self).get_context_data(**kwargs)

        problem = get_object_or_404(Problem, codename=self.kwargs['slug'])
        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])

        if problem not in contest.problems.all():
            raise Http404

        user = self.request.user
        if not user.has_perm('view_contest', contest):
            raise PermissionDenied
        else:
            context['problem'] = problem
            context['contest'] = contest
            return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        problem = get_object_or_404(Problem, codename=self.kwargs['slug'])
        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])

        if problem not in contest.problems.all():
            raise Http404
        elif not contest.is_active:
            raise PermissionDenied

        user = self.request.user
        if not user.has_perm('view_contest', contest):
            raise PermissionDenied
        else:
            form.instance.problem = problem
            form.instance.contest = contest
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

    def get_object(self):
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
            printRequest = PrintRequest(
                source=submission.source,
                language=submission.language,
                contest=submission.contest,
                author=submission.author,
                problem=submission.problem)
            printRequest.save()
            success(request, _("Print request added to print queue."))

        return redirect('submission', int(self.kwargs['pk']))


class ProblemPrintView(View):

    def get(self, request, *args, **kwargs):
        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])
        problem = get_object_or_404(Problem, codename=self.kwargs['slug'])

        if problem not in contest.problems.all():
            raise Http404

        user = self.request.user
        if not user.has_perm('view_contest', contest):
            raise PermissionDenied
        elif not contest.is_started and not user.is_superuser:
            raise Http404

        if not contest.is_printing_available:
            error(request, _("Printing not available."))
        else:
            source = "{}\n{}".format(problem.name, strip_tags(problem.content))
            for sampleio in problem.sampleio_set.all():
                source = string_concat(source, _("Input"), ':\n',
                                       strip_tags(sampleio.input), '\n\n')
                source = string_concat(source, _("Output"), ':\n',
                                       strip_tags(sampleio.output), '\n\n')
            printRequest = PrintRequest(
                source=source,
                language='plain',
                author=user,
                contest=contest,
                problem=problem)
            printRequest.save()
            success(request, _("Print request added to print queue."))

        return redirect('problem', self.kwargs['contest_pk'],
                        self.kwargs['slug'])


class SubmissionPrintCreateView(FormView):

    model = PrintRequest
    form_class = PrintRequestForm
    template_name = 'print_submission_form.html'
    success_url = '../'

    def get_context_data(self, **kwargs):
        context = super(
            SubmissionPrintCreateView, self).get_context_data(**kwargs)

        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])

        user = self.request.user
        if not user.has_perm('view_contest', contest) or \
           not contest.is_printing_available or not contest.is_active:
            raise PermissionDenied
        context['contest'] = contest
        return context

    def form_valid(self, form):
        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])

        user = self.request.user
        if not user.has_perm('view_contest', contest) or \
           not contest.is_printing_available:
            raise PermissionDenied

        printRequest = PrintRequest(
            source=form.cleaned_data['source'],
            language=form.cleaned_data['language'],
            contest=contest,
            author=user)
        printRequest.save()

        if not contest.is_printing_available:
            error(self.request, _("Printing not available."))
        else:
            success(self.request, _("Print request added to print queue."))

        return super(SubmissionPrintCreateView, self).form_valid(form)


class ScoreRankingListView(TemplateView):

    template_name = 'ranking_list.html'
    context_object_name = 'ranking_list'

    def get_context_data(self, **kwargs):
        context = super(ScoreRankingListView, self).get_context_data(**kwargs)
        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])
        user = self.request.user

        if not user.has_perm('view_contest', contest):
            raise PermissionDenied

        includeFreezed = True

        if self.request.user.is_superuser or \
           user.has_perm('see_unfrozen_ranking', contest):
            includeFreezed = False

        problems, users = contest.getProblemsAndLastUsersSubmissions(
            includeFreezed)

        if len(users) == 0:
            return dict({'empty': True, 'contest': contest})

        context['problem_list'] = problems
        context['ranking_list'] = users
        context['contest'] = contest

        if contest.team:
            self.template_name = 'ranking_time_list.html'
            begin_time = contest.start_time
            for dummy, user in context['ranking_list'].items():
                user.score = 0
                user.totalTime = timedelta()
                for dummy, problem in user.problems.items():
                    if problem.score < 100:
                        problem.score = 0
                        problem.timestamp = "-"
                    else:
                        problem.timestamp = problem.timestamp
                        - begin_time + timedelta(minutes=((problem.total - 1) *
                                                          contest.penalty))
                        user.score += 1
                        user.totalTime += problem.timestamp

        context['ranking_list'] = OrderedDict(
            sorted(users.items(), key=lambda t: (-t[1].score, t[1].totalTime)))

        return context


class PDFTemplateResponse(TemplateResponse):

    def generate_pdf(self, *args):
        html = self.content.decode('utf-8')
        result = StringIO.StringIO()
        rendering = pisa.pisaDocument(StringIO.StringIO(html.encode('utf-8')),
                                      result, encoding='utf-8')
        if rendering.err:
            return HttpResponse(escape(html))
        else:
            self.content = result.getvalue()

    def __init__(self, *args, **kwargs):
        kwargs['content_type'] = 'application/pdf'
        super(PDFTemplateResponse, self).__init__(*args, **kwargs)
        self.add_post_render_callback(self.generate_pdf)


class PDFTemplateView(TemplateView):
    response_class = PDFTemplateResponse


class ProblemPDFView(PDFTemplateView):
    template_name = 'problem_detail_pdf.html'

    def get_context_data(self, **kwargs):
        problem = get_object_or_404(Problem,
                                    codename=self.kwargs['slug'])
        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])

        if problem not in contest.problems.all():
            raise Http404

        user = self.request.user
        if not user.has_perm('view_contest', contest):
            raise PermissionDenied
        elif not contest.is_started and not user.is_superuser:
            raise Http404

        return super(ProblemPDFView, self).get_context_data(
            problem=problem,
            **kwargs
        )
