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

from django.conf.urls.defaults import patterns, include
from django.contrib import admin

admin.autodiscover()

handler500 = 'django.views.defaults.server_error'

urlpatterns = patterns('',
    (r'^admin/' , include(admin.site.urls)),
)