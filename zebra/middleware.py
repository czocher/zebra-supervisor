from django.conf import settings
from django.http import HttpResponseRedirect

import re


class RequireLoginMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.urls = tuple(
            [re.compile(url) for url in settings.LOGIN_REQUIRED_URLS])
        self.require_login_path = getattr(
            settings, 'LOGIN_URL', '/accounts/login/')

    def __call__(self, request):
        for url in self.urls:
            if url.match(request.path) and request.user.is_anonymous:
                return HttpResponseRedirect(
                    '{}?next={}'.format(self.require_login_path, request.path))
        return self.get_response(request)
