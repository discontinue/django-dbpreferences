# coding: utf-8


"""
    dbpreferences base form
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2011 by the django-dbpreferences team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import warnings

from django import forms
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.forms.fields import BooleanField

from dbpreferences.models import Preference
from dbpreferences.tools import forms_utils, easy_import


class DBPreferencesBaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        assert(isinstance(self.Meta.app_label, basestring))
        super(DBPreferencesBaseForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if field.__class__.__name__.startswith("Model"):
                msg = (
                    "Error with field %r from %r:"
                    " Form fields which handle relationships are not supported, yet."
                ) % (name, self.Meta.app_label)
                raise AssertionError(msg)

    def _get_app_label_form_name(self):
        app_label = self.Meta.app_label
        form_name = self.__class__.__name__
        return app_label, form_name

    def save_form_init(self):
        current_site = Site.objects.get_current()
        app_label, form_name = self._get_app_label_form_name()

        try:
            Preference.objects.get(site=current_site, app_label=app_label, form_name=form_name).delete()
        except Preference.DoesNotExist:
            pass

        # Save initial form values into database
        self.instance, form_dict = Preference.objects.save_form_init(
            form=self, site=current_site, app_label=app_label, form_name=form_name)

        return form_dict

    def __setitem__(self, key, value):
        if self.data == {}:
            # set self.data with the preferences values
            self.get_preferences()

        self.data[key] = value

    def save(self):
        self.instance.preferences = self.data
        self.instance.save()

    def full_clean(self):
        """
        Fill missing values with initial data and create a warning for that.
        XXX: Is this the best place to do this?
        """
        for name, field in self.fields.items():
            if name not in self.data and field.initial:

                if isinstance(field, BooleanField):
                    # BooleanFields can be missed (unchecked) ;)
                    continue

                # Field doesn't exist in current preferences. Add it if initial value given
                initial = field.initial
                self.data[name] = initial
                app_label, form_name = self._get_app_label_form_name()
                msg = (
                    "Use initial value %r for %r cause"
                    " it didn't exist in %s.%s preferences, yet."
                ) % (initial, name, app_label, form_name)
                warnings.warn(msg)

        super(DBPreferencesBaseForm, self).full_clean()

    def get_preferences(self):
        """
        return current preferences
            1. get the dbpreferenced data from database
            2. validate them
            3. return cleaned_data dict
        """
        try:
            self.instance = self.get_db_instance()
        except Preference.DoesNotExist:
            self.data = self.save_form_init()
        else:
            self.data = self.instance.preferences

        # Cleans all of self.data and populates self._errors and self.cleaned_data
        self.is_bound = True
        self.full_clean()

        if not self.is_valid():
            errors = []
            for item, msg in self._errors.iteritems():
                if item in self.data:
                    value_info = "(current value is: %r)" % self.data[item]
                else:
                    value_info = "(key not set in dict!)"

                errors.append(
                    "'%s' %s: '%s'" % (
                        item, value_info, ", ".join(msg)
                    )
                )

            error_msg = ", ".join(errors)
            app_label, form_name = self._get_app_label_form_name()
            raise ValidationError(
                "DBpreferences data for '%s.%s' not valid: %s" % (
                    app_label, form_name, error_msg
                )
            )

        return self.cleaned_data

    def get_db_instance(self):
        """ returns the database entry instance """
        current_site = Site.objects.get_current()
        app_label = self.Meta.app_label
        form_name = self.__class__.__name__

        self.instance = Preference.objects.get(site=current_site, app_label=app_label, form_name=form_name)
        return self.instance
