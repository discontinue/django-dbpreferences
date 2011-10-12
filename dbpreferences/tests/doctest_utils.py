#!/usr/bin/env python
# coding: utf-8

"""
    run all unittests
    ~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by django-dbpreferences team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import division, absolute_import

import os

if __name__ == "__main__":
    # run unittest directly
    os.environ["DJANGO_SETTINGS_MODULE"] = "test_settings"

from doctest import testmod
import sys
import unittest

import dbpreferences




SKIP_DIRS = (".settings", ".git", "dist")
SKIP_FILES = ("setup.py", "test.py")


def run_all_doctests():
    path = os.path.abspath(os.path.dirname(dbpreferences.__file__))
    print
    print "_" * 79
    print "Running %r DocTests:\n" % path

    total_files = 0
    total_doctests = 0
    total_attempted = 0
    total_failed = 0
    for root, dirs, filelist in os.walk(path, followlinks=True):
        for skip_dir in SKIP_DIRS:
            if skip_dir in dirs:
                dirs.remove(skip_dir) # don't visit this directories

        for filename in filelist:
            if not filename.endswith(".py"):
                continue
            if filename in SKIP_FILES:
                continue

            total_files += 1

            sys.path.insert(0, root)
            try:
                m = __import__(filename[:-3])
            except ImportError, err:
                print "***DocTest import %s error*** %s" % (filename, err)
            except Exception, err:
                print "***DocTest %s error*** %s" % (filename, err)
            else:
                failed, attempted = testmod(m)
                total_attempted += attempted
                total_failed += failed
                if attempted or failed:
                    total_doctests += 1

                if attempted and not failed:
                    filepath = os.path.join(root, filename)
                    print "DocTest in %s OK (failed=%i, attempted=%i)" % (
                        filepath, failed, attempted
                    )
            finally:
                del sys.path[0]
    print "*** %i files readed, runs %i doctests: failed=%i, attempted=%i" % (
        total_files, total_doctests, total_failed, total_attempted
    )


if __name__ == '__main__':
    run_all_doctests()

    print
    print "_" * 79
    print "Running Unittests:\n"

    unittest.main(
#        verbosity=99
    )
elif "test" in sys.argv:
    # e.g.: .../vdpreferences$ ./setup.py test
    run_all_doctests()
