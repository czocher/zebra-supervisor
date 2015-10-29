# -*- coding: utf-8 -*-
"""This module contains functions to make submission score loading easier."""
from django import template

register = template.Library()


@register.inclusion_tag('submission_score_loader.html')
def submission_score_loader(submission):
    """Insert a html ajax submission score loader."""
    return {'submission': submission}
