from django.conf.urls import patterns, url

from views import SessionGetView, SessionEndView, ReportView, SubmissionView,\
    TestView, TestTimestampView

urlpatterns = patterns('',
    url(r'^getsession/nodename/(?P<nodeName>[\w]+)/nodekey/(?P<nodeKey>[\w]+)/$',
        SessionGetView.as_view()),

    url(r'^endsession/sessionid/(?P<sessionId>[\w]{8}(-[\w]{4}){3}-[\w]{12})/$',
        SessionEndView.as_view()),

    url(r'^postreport/sessionid/(?P<sessionId>[\w]{8}(-[\w]{4}){3}-[\w]{12})/$',
        ReportView.as_view()),

    url(r'^getconfig/sessionid/(?P<sessionId>[\w]{8}(-[\w]{4}){3}-[\w]{12})/$',
        ReportView.as_view()),

    url(r'^getsubmission/sessionid/(?P<sessionId>[\w]{8}(-[\w]{4}){3}-[\w]{12})/$',
        SubmissionView.as_view()),

    url(r'^postsubmission/sessionid/(?P<sessionId>[\w]{8}(-[\w]{4}){3}-[\w]{12})/submissionid/(?P<submissionId>\d+)/$',
        SubmissionView.as_view()),

    url(r'^gettesttimestamps/sessionid/(?P<sessionId>[\w]{8}(-[\w]{4}){3}-[\w]{12})/problemid/(?P<problemId>[-\w]+)/$',
        TestTimestampView.as_view()),

    url(r'^gettests/sessionid/(?P<sessionId>[\w]{8}(-[\w]{4}){3}-[\w]{12})/problemid/(?P<problemId>[-\w]+)/(?P<type>(in|out|conf))/$',
        TestView.as_view()),
)
