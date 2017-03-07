# -*- coding: utf-8 -*-
from django.views.generic import TemplateView

from datetime import timedelta
from collections import OrderedDict

from .mixins import ValidRequestMixin


class ScoreRankingListView(ValidRequestMixin, TemplateView):

    template_name = 'ranking_list.html'
    context_object_name = 'ranking_list'

    def get_context_data(self, **kwargs):
        context = super(ScoreRankingListView, self).get_context_data(**kwargs)

        include_freezed = True
        user = self.request.user
        if user.is_staff or \
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
