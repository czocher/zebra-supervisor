from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404

from django.db.models import Q
from questions.models import Question
from questions.forms import QuestionForm
from judge.models import Contest


class ContestCreateQuestionView(CreateView):
    template_name = 'question_form.html'
    model = Question
    form_class = QuestionForm

    def get_form_kwargs(self):
        kwargs = super(ContestCreateQuestionView, self).get_form_kwargs()
        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])
        kwargs.update({'contest': contest})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ContestCreateQuestionView, self).get_context_data(
            **kwargs)
        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])
        context['contest'] = contest
        return context

    def post(self, request, *args, **kwargs):
        self.success_url = '/judge/contest/%s/questions/' % (
            kwargs['contest_pk'], )
        return super(ContestCreateQuestionView,
                     self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])

        user = self.request.user
        if not user.has_perm('view_contest', contest):
            raise PermissionDenied
        else:
            self.initial['request'] = self.request

        return super(ContestCreateQuestionView,
                     self).get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])
        if form.instance.problem is not None \
           and form.instance.problem not in contest.problems.all():
            raise Http404

        form.instance.contest = contest
        return super(ContestCreateQuestionView, self).form_valid(form)


class ContestQuestionListView(ListView):
    template_name = 'question_list.html'
    context_object_name = 'question_list'
    model = Question
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super(ContestQuestionListView,
                        self).get_context_data(**kwargs)
        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])
        context['contest'] = contest
        return context

    def get_queryset(self):
        questions = super(ContestQuestionListView, self).get_queryset()
        contest = get_object_or_404(Contest, pk=self.kwargs['contest_pk'])

        user = self.request.user
        if not user.has_perm('view_contest', contest):
            raise PermissionDenied

        questions = questions.filter(Q(author=self.request.user)
                                     | Q(public=True), Q(contest=contest))
        return questions


class ContestQuestionDetailView(DetailView):

    template_name = 'question_detail.html'
    context_object_name = 'question'
    model = Question

    def get_object(self):
        question = super(ContestQuestionDetailView, self).get_object()

        if question.author != self.request.user and not question.public:
            raise PermissionDenied
        else:
            if question.is_answered:
                question.readBy.add(self.request.user)
            return question
