# -*- coding: utf-8 -*-
"""This module contains url patterns for the rest app."""
from django.conf.urls import url, include
from .views import ROUTER

urlpatterns = [
    url(r'^', include(ROUTER.urls)),
]
