# -*- coding: utf-8 -*-
"""This module contains url patterns for the judge app."""
from django.conf.urls import include, url

from .views import ContestListView, ContestDetailView, ProblemDetailView, \
    ScoreRankingListView, SubmissionCreateView, ContestSubmissionListView, \
    SubmissionListView, SubmissionPrintView, SubmissionDetailView, \
    SubmissionPrintCreateView, LatestContestSubmissionsTemplateView,\
    ProblemPDFView

urlpatterns = [
    url(r'^$', ContestListView.as_view(), name='contests'),

    url(r'^contest/(?P<contest_pk>\d+)/', include([
        url(r'^$',
            ContestDetailView.as_view(), name='contest'),

        url(r'^problem/(?P<slug>[\w\-_]+)/$',
            ProblemDetailView.as_view(), name='problem'),

        url(r'^problem/(?P<slug>[\w\-_]+)/pdf$',
            ProblemPDFView.as_view(), name='pdfProblem'),

        url(r'^ranking/$',
            ScoreRankingListView.as_view(), name='ranking'),

        url(r'^problem/(?P<slug>[\w\-_]+)/submit/$',
            SubmissionCreateView.as_view()),

        url(r'^submissions/$',
            ContestSubmissionListView.as_view(), name='contestSubmissions'),

        url(r'^submissions/latest/$',
            LatestContestSubmissionsTemplateView.as_view(),
            name='latestContestSubmissions'),

        url(r'^print/$',
            SubmissionPrintCreateView.as_view(), name='printSourceCode'),

        url(r'^questions/', include('questions.urls')),
    ])),

    url(r'^submissions/', include([
        url(r'^$',
            SubmissionListView.as_view(), name='submissions'),

        url(r'^(?P<pk>\d+)/print/',
            SubmissionPrintView.as_view(), name='printSubmission'),

        url(r'^(?P<pk>\d+)/$',
            SubmissionDetailView.as_view(), name='submission'),
    ])),

]
