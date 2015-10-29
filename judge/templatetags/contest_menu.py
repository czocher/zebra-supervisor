# -*- coding: utf-8 -*-
"""This module contains functions to manage the contest menu."""
from django.db.models import Q
from django import template

register = template.Library()


@register.inclusion_tag('contest_menu.html')
def contest_menu(contest, user):
    """Load and fill the contest menu for the given user."""
    submissions = contest.submissions.filter(author=user)
    questions = contest.questions.filter(Q(author=user) | Q(public=True))
    return {'contest': contest, 'user': user,
            'questions': questions, 'submissions': submissions}
