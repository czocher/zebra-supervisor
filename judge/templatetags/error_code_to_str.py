from django import template
from django.utils.translation import ugettext_lazy as _


register = template.Library()


@register.filter
def error_code_to_str(code):
    if code == 0:
        return _("Ok")
    elif code == 6:
        return _("Abnormal program termination")
    elif code == 8:
        return _("Floating point exception")
    elif code == 9:
        return _("Timelimit")
    elif code == 11:
        return _("Segmentation fault")
