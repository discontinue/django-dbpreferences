#!/usr/bin/env python
# coding: utf-8

"""
    run unittests
    ~~~~~~~~~~~~~

    run all tests:

    ./runtests.py

    run only some tests, e.g.:

    ./runtests.py tests.test_file
    ./runtests.py tests.test_file.test_class
    ./runtests.py tests.test_file.test_class.test_method

    :copyleft: 2015 by the django-reversion-compare team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function

import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = os.environ.get(
    'DJANGO_SETTINGS_MODULE', "test_project.settings"
)

import django
from django.conf import settings
from django.test.utils import get_runner


def run_unittests(test_labels=None):
    print("Django v%s" % django.get_version())

    # keep debug print() "in sync" with stderr output:
    sys.stdout = sys.stderr

    if hasattr(django, "setup"):
        django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(
        verbosity=2,
        # failfast=True,
    )

    if test_labels is None or test_labels == ["test"]:
        test_labels = ['tests']

    failures = test_runner.run_tests(test_labels)
    sys.exit(bool(failures))


def cli_run():
    if "-v" in sys.argv or "--verbosity" in sys.argv:
        print("DJANGO_SETTINGS_MODULE=%r" % os.environ['DJANGO_SETTINGS_MODULE'])

    test_labels=[label for label in sys.argv[1:] if not label.startswith("-")]
    run_unittests(test_labels)


if __name__ == "__main__":
    cli_run()


