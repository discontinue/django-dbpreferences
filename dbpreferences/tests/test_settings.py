# coding: utf-8

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    
    'dbpreferences',
)

DATABASE_ENGINE = "sqlite3"
DATABASE_NAME = ":memory:"

SITE_ID = 1

ROOT_URLCONF = "dbpreferences.tests.test_urls"

import dbpreferences, django

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(dbpreferences.__file__), "templates/"),
    os.path.join(os.path.dirname(django.__file__), "contrib/admin/templates"),
)