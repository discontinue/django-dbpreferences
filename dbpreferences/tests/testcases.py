# coding: utf-8
"""
    Unittest for DBpreferences
    
    INFO: dbpreferences should be exist in python path!
"""

if __name__ == "__main__":
    # run unittest directly
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "test_settings"

from django import forms
from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse

from dbpreferences.models import Preference
from dbpreferences.forms import DBPreferencesBaseForm
from dbpreferences.tests.unittest_base import BaseTestCase
from dbpreferences.tests.preference_forms import UnittestForm

class FormWithoutMeta(DBPreferencesBaseForm):
    pass

class FormMetaWithoutAppLabel(DBPreferencesBaseForm):
    class Meta:
        pass





class TestDBPref(BaseTestCase):
    def setUp(self):
        Preference.objects.all().delete()

    def test_form_without_meta(self):
        self.failUnlessRaises(AttributeError, FormWithoutMeta)

    def test_form_meta_without_app_label(self):
        self.failUnlessRaises(AttributeError, FormMetaWithoutAppLabel)

    def test_form_api(self):
        form = UnittestForm()
        # Frist time, the data would be inserted into the database
        self.failUnless(Preference.objects.count() == 0)
        pref_data = form.get_preferences()
        self.failUnless(Preference.objects.count() == 1)
        self.failUnless(isinstance(pref_data, dict),
            "It's not dict, it's: %s - %r" % (type(pref_data), pref_data))
        self.failUnlessEqual(pref_data,
            {'count': 10, 'foo_bool': True, 'font_size': 0.7, 'subject': 'foobar'})

        form = UnittestForm()
        self.failUnless(Preference.objects.count() == 1)
        pref_data = form.get_preferences()
        self.failUnless(Preference.objects.count() == 1)
        self.failUnless(isinstance(pref_data, dict),
            "It's not dict, it's: %s - %r" % (type(pref_data), pref_data))
        self.failUnlessEqual(pref_data,
            {'count': 10, 'foo_bool': True, 'font_size': 0.7, 'subject': 'foobar'})

        # Change a value
        form["count"] = 20
        form.save()

        # Change a value without 
        form = UnittestForm()
        form["foo_bool"] = False
        form.save()

        # Check the changes value
        form = UnittestForm()
        pref_data = form.get_preferences()
        self.failUnlessEqual(pref_data,
            {'count': 20, 'foo_bool': False, 'font_size': 0.7, 'subject': 'foobar'})

    def test_admin_edit(self):
        # Create one db entry
        form = UnittestForm()
        pref_data = form.get_preferences()
        self.failUnless(Preference.objects.count() == 1)

        pk = Preference.objects.all()[0].pk
        url = reverse("admin_dbpref_edit_form", kwargs={"pk":pk})

        self.login(usertype="staff")

        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=("Change Preferences for", "dbpreferences.tests.UnittestForm"),
            must_not_contain=("Error", "Traceback")
        )

        response = self.client.post(url, data={
            "subject": "new content", "count": 5, "font_size": 1, "_save":"Save"})
        self.failUnlessEqual(response.status_code, 302)

        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=("Change Preferences for", "dbpreferences.tests.UnittestForm"),
            must_not_contain=("Error", "Traceback")
        )

        form = UnittestForm()
        self.failUnless(Preference.objects.count() == 1)
        pref_data = form.get_preferences()
        self.failUnless(Preference.objects.count() == 1)
        self.failUnless(isinstance(pref_data, dict),
            "It's not dict, it's: %s - %r" % (type(pref_data), pref_data))
        self.failUnlessEqual(pref_data,
            {'count': 5, 'foo_bool': False, 'font_size': 1.0, 'subject': u"new content"})


if __name__ == "__main__":
    # Run this unittest directly
    from django.core import management
    management.call_command('test', 'dbpreferences')
