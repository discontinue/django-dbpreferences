# coding: utf-8

"""
    DBPreferences - models
    ~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

if __name__ == "__main__":
    # For doctest only
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

import sys
import pprint

from django import forms
from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group

from dbpreferences.tools import forms_utils, easy_import, data_eval
from dbpreferences.fields import DictField

# The filename in witch the form should be stored:
PREF_FORM_FILENAME = "preference_forms"


def serialize(data):
    return pprint.pformat(data)

def deserialize(stream):
    return data_eval.data_eval(stream)


class PreferencesManager(models.Manager):
    """ Manager class for Preference model """
    def save_form_init(self, form, site, app_label, form_name):
        """ save the initial form values as the preferences into the database """
        form_dict = forms_utils.get_init_dict(form)
        new_entry = Preference(
            site=site,
            app_label=app_label,
            form_name=form_name,
            preferences=form_dict,
        )
        new_entry.save()
        return new_entry, form_dict

    def get_pref(self, form):
        """
        returns the preferences for the given form
        stores the preferences into the database, if not exist.
        """
        assert isinstance(form, forms.Form), ("You must give a form instance and not only the class!")

        current_site = Site.objects.get_current()
        app_label = form.Meta.app_label
        form_name = form.__class__.__name__

        try:
            db_entry = self.get(site=current_site, app_label=app_label, form_name=form_name)
        except Preference.DoesNotExist:
            # Save initial form values into database
            form_dict = self.save_form_init(form, current_site, app_label, form_name)
        else:
            form_dict = db_entry.preferences

        return form_dict


class Preference(models.Model):
    """
    Plugin preferences
    """
    objects = PreferencesManager()

    id = models.AutoField(primary_key=True, help_text="The id of this preference entry, used for lucidTag")

    site = models.ForeignKey(Site, editable=False, verbose_name=_('Site'))
    app_label = models.CharField(max_length=128, editable=False,
        help_text="app lable, must set via form.Meta.app_label")
    form_name = models.CharField(max_length=128, editable=False,
        help_text="preference form class name")

    preferences = DictField(null=False, blank=False, #editable=False,
        help_text="serialized preference form data dictionary")

    createtime = models.DateTimeField(auto_now_add=True, help_text="Create time",)
    lastupdatetime = models.DateTimeField(auto_now=True, help_text="Time of the last change.",)
    lastupdateby = models.ForeignKey(User, editable=False, null=True, blank=True,
        related_name="%(class)s_lastupdateby", help_text="User as last edit the current page.",)

    def get_form_class(self):
        """ returns the form class for this preferences item """
        from_name = "%s.%s" % (self.app_label, PREF_FORM_FILENAME)
        form = easy_import.import3(from_name, self.form_name)
        return form

    def __unicode__(self):
        return u"Preferences for %s.%s.%s" % (self.site, self.app_label, self.form_name)

    class Meta:
        unique_together = ("site", "app_label", "form_name")
        permissions = (("can_change_preferences", "Can change preferences"),)
        ordering = ("site", "app_label", "form_name")
        verbose_name = verbose_name_plural = "preferences"


#-----------------------------------------------------------------------------

_USER_SETTINGS_CACHE = {}

class UserSettingsManager(models.Manager):
    def get_settings(self, user):
        """ Cached access for getting UserSettings instance and settings. """
        if not user.is_authenticated():
            raise UserSettings.DoesNotExist("No settings for anonymous!")

        try:
            (user_settings_instance, user_settings) = _USER_SETTINGS_CACHE[user.pk]
        except KeyError:
            user_settings_instance = self.get(user=user)
            user_settings = user_settings_instance.get_settings()
            _USER_SETTINGS_CACHE[user.pk] = (user_settings_instance, user_settings)

        return user_settings_instance, user_settings


class UserSettings(models.Model):
    objects = UserSettingsManager()

    user = models.ForeignKey(User, unique=True, related_name="%(class)s_user")
    settings = DictField(null=False, blank=False,
        help_text="serialized user settings data dictionary")

    createtime = models.DateTimeField(auto_now_add=True, help_text="Create time",)
    createby = models.ForeignKey(User, editable=False,
        related_name="%(class)s_createby", help_text="User how has create this entry.",)
    lastupdatetime = models.DateTimeField(auto_now=True, help_text="Time of the last change.",)
    lastupdateby = models.ForeignKey(User, editable=False,
        related_name="%(class)s_lastupdateby", help_text="User how has last edit this entry.",)

    def save(self, *args, **kwargs):
        """ save and update the cache """
        _USER_SETTINGS_CACHE[self.user.pk] = (self, self.settings) # Update cache
        return super(UserSettings, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"UserSettings for %r: %r" % (self.user, self.settings)

    class Meta:
        ordering = ("user",)
        verbose_name = verbose_name_plural = "User settings"


if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
