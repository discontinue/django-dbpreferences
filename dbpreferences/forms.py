# coding: utf-8

from django import forms
from django.contrib.sites.models import Site

from dbpreferences.models import Preference
from dbpreferences.tools import forms_utils, easy_import

class DBPreferencesBaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        assert(isinstance(self.Meta.app_label, basestring))
        super(DBPreferencesBaseForm, self).__init__(*args, **kwargs)
        
    def get_preferences(self):
        current_site = Site.objects.get_current()
        app_label = self.Meta.app_label
        form_name = self.__class__.__name__
        
        try:
            db_entry = Preference.objects.get(site=current_site, app_label=app_label, form_name=form_name)
        except Preference.DoesNotExist:
            # Save initial form values into database
            form_dict = Preference.objects.save_form_init(
                form=self, site=current_site, app_label=app_label, form_name=form_name)
        else:
            form_dict = db_entry.preferences
        
        return form_dict