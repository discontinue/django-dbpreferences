# coding: utf-8

import os
import sys

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "dbpreferences.tests.test_settings"
    import dbpreferences.tests.test_settings

from django.conf import settings
from django.test.utils import get_runner
from django.contrib import admin

from dbpreferences.models import Preference


def runtests():
    admin.site.unregister(Preference)

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True)
    failures = test_runner.run_tests(['dbpreferences'])
    sys.exit(bool(failures))


if __name__ == "__main__":
    # Run this unittest directly
    runtests()
