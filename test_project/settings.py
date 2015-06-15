# coding: utf-8

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

DEBUG = True

SECRET_KEY = "Only for unittests!"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ":memory:"
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'dbpreferences',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'dbpreferences.middleware.DBPreferencesMiddleware',
)

SITE_ID = 1

STATIC_URL = "/static/"

ROOT_URLCONF = "test_project.urls"

import dbpreferences, django

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(dbpreferences.__file__), "templates/"),
    os.path.join(os.path.dirname(django.__file__), "contrib/admin/templates"),
)
