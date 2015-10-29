from django import template

register = template.Library()


@register.inclusion_tag('submission_score_loader.html')
def submission_score_loader(submission):
    return {'submission': submission}
