# coding: utf-8

"""
    unittest url patterns
    ~~~~~~~~~~~~~~~~~~~~~


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author:$

    :copyleft: 2009 by the django-dbpreferences team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

from dbpreferences.tests.test_views import test_user_settings, test_user_settings_cache

admin.autodiscover()

handler500 = 'django.views.defaults.server_error'

urlpatterns = patterns('',
    url(r'^admin/' , include(admin.site.urls)),
    url(r'^test_user_settings/(?P<test_name>.*)/(?P<key>.*)/(?P<value>.*)$',
        test_user_settings, name='test_user_settings'
    ),
    url(r'^test_user_settings_cache/(?P<no>\d)/$', test_user_settings_cache,
        name='test_user_settings_cache'),
)
