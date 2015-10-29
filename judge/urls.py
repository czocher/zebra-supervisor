# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from judge.views import ContestListView, ContestDetailView, \
    ProblemDetailView, ScoreRankingListView, SubmissionCreateView, \
    ContestSubmissionListView, SubmissionListView, SubmissionPrintView, \
    SubmissionDetailView, SubmissionPrintCreateView, ProblemPrintView, \
    ProblemPDFView

urlpatterns = [
    url(r'^$', ContestListView.as_view(), name='contests'),

    url(r'^contest/(?P<contest_pk>\d+)/', include([
        url(r'^$',
            ContestDetailView.as_view(), name='contest'),

        url(r'^problem/(?P<slug>[\w\-_]+)/$',
            ProblemDetailView.as_view(), name='problem'),

        url(r'^problem/(?P<slug>[\w\-_]+)/print$',
            ProblemPrintView.as_view(),
            name='printProblem'),

        url(r'^problem/(?P<slug>[\w\-_]+)/pdf$',
            ProblemPDFView.as_view(),
            name='pdfProblem'),

        url(r'^ranking/$',
            ScoreRankingListView.as_view(), name='ranking'),

        url(r'^problem/(?P<slug>[\w\-_]+)/submit/$',
            SubmissionCreateView.as_view()),

        url(r'^submissions/$',
            ContestSubmissionListView.as_view(
            ), name='contestSubmissions'),

        url(r'^print/$',
            SubmissionPrintCreateView.as_view(
            ), name='printSourceCode'),

        url(r'^questions/',
            include('questions.urls')),
    ])),

    url(r'^submissions/', include([
        url(r'^$',
            SubmissionListView.as_view(), name='submissions'),

        url(r'^print/$',
            SubmissionPrintView.as_view(
            ), name='printSubmission'),

        url(r'^(?P<pk>\d+)/$',
            SubmissionDetailView.as_view(), name='submission'),
    ])),

]
