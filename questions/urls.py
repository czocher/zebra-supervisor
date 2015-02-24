# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from questions.views import ContestQuestionListView,\
    ContestCreateQuestionView, ContestQuestionDetailView

urlpatterns = patterns('',
    url(r'^$',
        ContestQuestionListView.as_view(), name='questions'),

    url(r'new/$',
        ContestCreateQuestionView.as_view(), name='new_question'),

    url(r'(?P<pk>[\w\-_]+)/$',
        ContestQuestionDetailView.as_view(), name='question'),
)
