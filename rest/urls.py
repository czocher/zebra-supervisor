# -*- coding: utf-8 -*-
"""This module contains url patterns for the rest app."""
from django.conf.urls import url, include

from .views import router

urlpatterns = [
    url(r'^', include(router.urls)),
]
