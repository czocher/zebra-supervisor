import os

from django.conf import settings
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper


USE_XSENDFILE = getattr(settings, 'DEBUG', True)


def sendfile(path):
    if not USE_XSENDFILE:
        response = HttpResponse()
        response['Content-Type'] = ''
        response['X-Sendfile'] = path
        return response

    wrapper = FileWrapper(file(path))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(path)
    return response
