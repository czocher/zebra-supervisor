# -*- coding: utf-8 -*-
from django.views.generic import RedirectView
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.i18n import JavaScriptCatalog
from django.conf import settings
import rest_framework

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'zebra.views.home', name='home'),
    # url(r'^zebra/', include('zebra.foo.urls')),

    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),

    url(r'^$', RedirectView.as_view(url='/judge/', permanent=True)),

    url(r'^judge/', include('judge.urls')),

    url(r'^rest/', include('rest.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),

    url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html'),
        name='login'),

    url(r'^logout/$', auth_views.logout_then_login, name='logout'),

    url(r'password_change/$',
        auth_views.PasswordChangeView.as_view(
            template_name='password_change.html'), name='password_change'),

    url(r'password_change_done/$', RedirectView.as_view(url='/',
        permanent=True), name='password_change_done'),

    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript_catalog'),
]

# Works only if DEBUG = True
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
