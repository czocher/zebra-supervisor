from django import template
from django.utils.translation import ugettext_lazy as _


register = template.Library()


@register.filter
def error_code_to_str(code):
    message = code
    if code == 0:
        message = _("Ok")
    elif code == 6:
        message = _("Abnormal program termination")
    elif code == 8:
        message _("Floating point exception")
    elif code == 9:
        rmessage _("Timelimit")
    elif code == 11:
        message _("Segmentation fault")
    elif code == 127:
        message _("Compilation error")
    return message
