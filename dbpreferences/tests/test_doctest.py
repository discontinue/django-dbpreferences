#!/usr/bin/env python
# coding: utf-8

"""
    run all unittests
    ~~~~~~~~~~~~~~~~~

    :copyleft: 2011-2015 by django-dbpreferences team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import division, absolute_import

import os
import doctest
import sys

import dbpreferences


SKIP_DIRS = (".settings", ".git", "dist", ".egg-info")
SKIP_FILES = ("setup.py", "test.py")


def get_all_doctests(base_path, verbose=False):
    modules = []
    for root, dirs, filelist in os.walk(base_path, followlinks=True):
        for skip_dir in SKIP_DIRS:
            if skip_dir in dirs:
                dirs.remove(skip_dir) # don't visit this directories

        for filename in filelist:
            if not filename.endswith(".py"):
                continue
            if filename in SKIP_FILES:
                continue

            sys.path.insert(0, root)
            try:
                module = __import__(filename[:-3])
            except ImportError as err:
                if verbose:
                    print(
                        "\tDocTest import %s error %s" % (filename, err),
                        file=sys.stderr
                    )
            except Exception as err:
                if verbose:
                    print(
                        "\tDocTest %s error %s" % (filename, err),
                        file=sys.stderr
                    )
            else:
                try:
                    suite = doctest.DocTestSuite(module)
                except ValueError: # has no docstrings
                    continue

                test_count = suite.countTestCases()
                if test_count<1:
                    if verbose:
                        print(
                            "\tNo DocTests in %r" % module.__name__,
                            file=sys.stderr
                        )
                    continue

                if verbose:
                    file_info = module.__file__
                else:
                    file_info = module.__name__
                print(
                    "\t%i DocTests in %r" % (test_count,file_info),
                    file=sys.stderr
                )
                modules.append(module)
            finally:
                del sys.path[0]

    return modules



def load_tests(loader, tests, ignore):
    print("\ncollect DocTests:", file=sys.stderr)
    path = os.path.abspath(os.path.dirname(dbpreferences.__file__))
    modules = get_all_doctests(
        base_path=path,
        # verbose=True
    )
    for module in modules:
        tests.addTests(doctest.DocTestSuite(module))
    return tests
