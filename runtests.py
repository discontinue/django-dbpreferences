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

from tests.runtests import cli_run

if __name__ == "__main__":
    cli_run()


