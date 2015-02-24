# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from judge.views import ContestListView, ContestDetailView, \
    ProblemDetailView, ScoreRankingListView, SubmissionCreateView, \
    ContestSubmissionListView, SubmissionListView, SubmissionPrintView, \
    SubmissionDetailView, SubmissionPrintCreateView, ProblemPrintView, \
    ProblemPDFView


urlpatterns = patterns('',
    url(r'^$', ContestListView.as_view(), name='contests'),

    url(r'^contest/(?P<pk>\d+)/$',
        ContestDetailView.as_view(), name='contest'),

    url(r'^contest/(?P<contest_pk>\d+)/problem/(?P<slug>[\w\-_]+)/$',
        ProblemDetailView.as_view(), name='problem'),

    url(r'^contest/(?P<contest_pk>\d+)/problem/(?P<slug>[\w\-_]+)/print$',
        ProblemPrintView.as_view(),
        name='printProblem'),

    url(r'^contest/(?P<contest_pk>\d+)/problem/(?P<slug>[\w\-_]+)/pdf$',
        ProblemPDFView.as_view(),
        name='pdfProblem'),

    url(r'^contest/(?P<contest_pk>\d+)/ranking/$',
        ScoreRankingListView.as_view(), name='ranking'),

    url(r'^contest/(?P<contest_pk>\d+)/problem/(?P<slug>[\w\-_]+)/submit/$',
        SubmissionCreateView.as_view()),

    url(r'^contest/(?P<contest_pk>\d+)/submissions/$',
        ContestSubmissionListView.as_view(
        ), name='contestSubmissions'),

    url(r'^contest/(?P<contest_pk>\d+)/print/$',
        SubmissionPrintCreateView.as_view(
        ), name='printSourceCode'),

    url(r'^submissions/$',
        SubmissionListView.as_view(), name='submissions'),

    url(r'^submissions/(?P<pk>\d+)/print/$',
        SubmissionPrintView.as_view(
        ), name='printSubmission'),

    url(r'^submissions/(?P<pk>\d+)/$',
        SubmissionDetailView.as_view(), name='submission'),

    url(r'^contest/(?P<contest_pk>\d+)/questions/',
        include('questions.urls')),

)
