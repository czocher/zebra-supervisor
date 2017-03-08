# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import ContestQuestionListView, ContestCreateQuestionView, \
    ContestQuestionDetailView


urlpatterns = [
    url(r'^$', ContestQuestionListView.as_view(), name='questions'),

    url(r'new/$', ContestCreateQuestionView.as_view(), name='question_new'),

    url(r'(?P<pk>[\w\-_]+)/$',
        ContestQuestionDetailView.as_view(), name='question'),
]
