# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404

from judge.models import Contest, Problem


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
        elif not self.contest.is_started and not user.is_staff:
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
