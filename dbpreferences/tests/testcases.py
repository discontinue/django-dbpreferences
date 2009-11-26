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
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser

from dbpreferences import models
from dbpreferences.middleware import SettingsDict
from dbpreferences.forms import DBPreferencesBaseForm
from dbpreferences.models import Preference, UserSettings
from dbpreferences.tests.unittest_base import BaseTestCase
from dbpreferences.tests.preference_forms import UnittestForm, TestModelChoiceForm
from dbpreferences.fields import DictField, DictData, DictFormField


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
        url = reverse("admin:dbpref_edit_form", kwargs={"pk":pk})

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

    def test_model_choice(self):
        """
        Test the form check: Form fields which handle relationships are not supported, yet.
        """
        self.failUnlessRaises(AssertionError, TestModelChoiceForm)

        # A test can look like this, if ModelChoiceField are supported:
#        form = TestModelChoiceForm()
#        pref_data = form.get_preferences()
#
#        pref_obj = Preference.objects.all()[0]
#        form["model_choice"] = pref_obj
#        form.save()
#
#        form = TestModelChoiceForm()
#
#        self.failUnlessEqual(form["model_choice"], pref_obj)


# ----------------------------------------------------------------------------


class TestDictFieldForm(BaseTestCase):
    """ Tests for dbpreferences.fields objects. """
    def test_data_eval1(self):
        d = DictField().to_python('''{"foo":"bar"}''')
        self.failUnlessEqual(d, {'foo': 'bar'})
        self.failUnless(isinstance(d, DictData))

    def test_repr1(self):
        """ use get_db_prep_save() with DictData instance """
        d = DictData({'foo': 'bar'})
        s = DictField().get_db_prep_save(d)
        self.failUnlessEqual(s, "{'foo': 'bar'}")

    def test_repr2(self):
        """ use get_db_prep_save() with normal dict object """
        s = DictField().get_db_prep_save({'foo': 'bar'})
        self.failUnlessEqual(s, "{'foo': 'bar'}")

    def test_to_python_cant_empty1(self):
        d = DictField()
        self.failUnlessRaises(forms.ValidationError, d.to_python, None)

    def test_to_python_cant_empty2(self):
        d = DictField(blank=True, null=False)
        self.failUnlessRaises(forms.ValidationError, d.to_python, None)

    def test_to_python_can_empty(self):
        d = DictField(blank=True, null=True)
        self.failUnlessEqual(d.to_python(None), None)

    def test_get_db_prep_save_cant_empty1(self):
        d = DictField()
        self.failUnlessRaises(forms.ValidationError, d.get_db_prep_save, None)

    def test_get_db_prep_save_cant_empty2(self):
        d = DictField(blank=True, null=False)
        self.failUnlessRaises(forms.ValidationError, d.get_db_prep_save, None)

    def test_get_db_prep_save_can_empty(self):
        d = DictField(blank=True, null=True)
        self.failUnlessEqual(d.get_db_prep_save(None), None)

    def test_formfield(self):
        d = DictField()
        f = d.formfield()
        self.failUnless(isinstance(f, DictFormField))

    def test_formfield_clean(self):
        f = DictFormField()
        d = f.clean('''{"foo":"bar"}''')
        self.failUnlessEqual(d, {'foo': 'bar'})

    def test_formfield_clean_cant_empty(self):
        f = DictFormField()
        self.failUnlessRaises(forms.ValidationError, f.clean, None)

    def test_formfield_clean_can_empty(self):
        f = DictFormField(required=False)
        s = f.clean(None)
        self.failUnlessEqual(s, u'')


# ----------------------------------------------------------------------------


class UserSettingsTestCache(dict):
    def __init__(self):
        self.cache_hit = 0
        super(UserSettingsTestCache, self).__init__()

    def __setitem__(self, key, value):
        assert isinstance(value, tuple) == True
        assert isinstance(key, int)
        assert isinstance(value[0], UserSettings)
        assert isinstance(value[1], dict)
        dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        self.cache_hit += 1
        return dict.__getitem__(self, key)


class TestUserSettings(BaseTestCase):
    def setUp(self):
        self._saved = 0
        self._init = 0
        signals.post_save.connect(self._post_save_handler, sender=UserSettings)
        signals.pre_init.connect(self._post_init_handler, sender=UserSettings)

        models._USER_SETTINGS_CACHE = UserSettingsTestCache()
        UserSettings.objects.all().delete()

    def _post_save_handler(self, **kwargs):
        self._saved += 1
    def _post_init_handler(self, **kwargs):
        self._init += 1

    def test_cache(self):
        """ Test if USER_SETTINGS_CACHE is UserSettingsTestCache witch has some assert statements """
        self.failUnless(isinstance(models._USER_SETTINGS_CACHE, UserSettingsTestCache))
        def test():
            models._USER_SETTINGS_CACHE["foo"] = "Bar"
        self.failUnlessRaises(AssertionError, test)

    def test_low_level(self):
        self.failUnlessEqual(len(models._USER_SETTINGS_CACHE), 0)

        user = self.get_user(usertype="staff")
        user_settings = SettingsDict(user)

        # .get set the value, if not exist 
        self.failUnlessEqual(user_settings.get("Foo", "initial value"), "initial value")
        self.failUnlessEqual(user_settings["Foo"], "initial value")

        # change the existing value
        user_settings["Foo"] = "new value"
        # Now we should get the new value:
        self.failUnlessEqual(user_settings.get("Foo", "initial value"), "new value")

        # before we save, nothing should be created
        self.failUnless(UserSettings.objects.count() == 0)

        self.failUnlessEqual(self._init, 0)
        self.failUnlessEqual(self._saved, 0)
        self.failUnlessEqual(len(models._USER_SETTINGS_CACHE), 0)

        user_settings.save() # increment: pre_init + post_save

        self.failUnlessEqual(self._init, 1)
        self.failUnlessEqual(self._saved, 1)
        self.failUnlessEqual(len(models._USER_SETTINGS_CACHE), 1)
        self.failUnless(user.pk in models._USER_SETTINGS_CACHE)
        self.failUnless(UserSettings.objects.count() == 1)

        instance = UserSettings.objects.get(user=user) # increment: pre_init
        self.failUnlessEqual(self._init, 2)
        self.failUnlessEqual(instance.settings, {"Foo": "new value"})

        # Now we should get a cached version, so pre_init should not be increment
        user_settings = SettingsDict(user)
        self.failUnlessEqual(user_settings["Foo"], "new value")

        self.failUnlessEqual(self._init, 2)
        self.failUnlessEqual(self._saved, 1)
        self.failUnlessEqual(models._USER_SETTINGS_CACHE.cache_hit, 2)

    def test_load(self):
        """
        The load() method in middleware.SettingsDict would be called on every get, getitem, etc.
        But the real loading should only done one time.
        """
        user = self.get_user(usertype="staff")
        user_settings = SettingsDict(user)
        self.failUnlessEqual(models._USER_SETTINGS_CACHE.cache_hit, 0)
        user_settings.get("foo", "bar")
        user_settings.get("foo", "bar")
        user_settings["foo"]
        user_settings["foo"]
        self.failUnlessEqual(models._USER_SETTINGS_CACHE.cache_hit, 1)

    def test_view_base(self):
        url = reverse("test_user_settings", kwargs={"test_name": "base_test", "key": "Foo", "value": "Bar"})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.content, "FooBar")

    def test_view_get(self):
        self.login(usertype="staff")

        # first access via .get() -> returned the default value "initial value"
        url = reverse("test_user_settings",
            kwargs={"test_name": "get", "key": "Foo", "value": "initial value"}
        )
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.content, "initial value")

        # change with .setitem()
        url = reverse("test_user_settings",
            kwargs={"test_name": "setitem", "key": "Foo", "value": "new value"}
        )
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.content, "new value")

        # now, the .get() method should returned the current value
        url = reverse("test_user_settings",
            kwargs={"test_name": "get", "key": "Foo", "value": "initial value"}
        )
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.content, "new value")

    def test_user_settings_cache(self):
        self.login(usertype="staff")
        for no in xrange(10):
            url = reverse("test_user_settings_cache", kwargs={"no": no})
            response = self.client.get(url)
            self.failUnlessEqual(response.status_code, 200)
            self.failUnlessEqual(response.content, str(no))

        self.failUnlessEqual(self._init, 2)
        self.failUnlessEqual(self._saved, 2)
        self.failUnlessEqual(models._USER_SETTINGS_CACHE.cache_hit, 10)

    def test_anonymous(self):
        """
        The settings would be not saved for anonymous users.
        We allways get the default value back.
        """
        user = AnonymousUser()

        user_settings = SettingsDict(user)
        user_settings["Foo"] = "bar"
        # in a request, we get values set in the past
        self.failUnlessEqual(user_settings["Foo"], "bar")

        # For anonymous user, save() does nothing:
        user_settings.save()
        self.failUnlessEqual(self._saved, 0)

        # In "the next request" we can't get the old value "bar"
        user_settings = SettingsDict(user)
        self.failUnlessEqual(user_settings.get("Foo", "not the initial value"), "not the initial value")






if __name__ == "__main__":
    # Run this unittest directly
    from django.core import management
    management.call_command('test', 'dbpreferences')
#    management.call_command('test', 'dbpreferences.TestDictFieldForm')
