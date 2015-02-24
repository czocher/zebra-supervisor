# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse
from django.core.servers.basehttp import FileWrapper


USE_XSENDFILE = getattr(settings, 'DEBUG', True)


def sendfile(path):
    if not USE_XSENDFILE:
        response = HttpResponse()
        response['Content-Type'] = ''
        response['X-Sendfile'] = path
        return response

    wrapper = FileWrapper(file(path))
    response = StreamingHttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(path)
    return response
