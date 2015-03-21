# -*- coding: utf-8 -*-
from django.views.generic import RedirectView
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
import rest_framework

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'zebra.views.home', name='home'),
    # url(r'^zebra/', include('zebra.foo.urls')),

    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),

    url(r'^$', RedirectView.as_view(url='/judge/')),

    url(r'^judge/', include('judge.urls')),

    url(r'^rest/', include('rest.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^login/$', 'django.contrib.auth.views.login', {
        'template_name': 'login.html', }),

    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),

    url(r'password_change/$', 'django.contrib.auth.views.password_change'),

    url(r'password_change_done/$', RedirectView.as_view(url='/'), name='password_change_done'),

    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)
