# coding: utf-8

"""
    DBPreferences - fields
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2011 by the dbpreferences team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import warnings

if __name__ == "__main__":
    # For doctest only
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

import sys
import pprint

from django import forms
from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group
from django.utils import six

from dbpreferences.tools import forms_utils, easy_import, data_eval
from dbpreferences.tools.data_eval import DataEvalError



class DictFormField(forms.CharField):
    """
    form field for preferences dict
    
    >>> DictFormField().clean('''{"foo":"bar"}''') == {'foo': 'bar'}
    True
    """
    def clean(self, value):
        """
        validate the form data
        FIXME: How can we get the pref form class for validating???
        """
        value = super(DictFormField, self).clean(value)
        if value == u'':
            # empty value with a required=False
            return u''

        try:
            return DictData(value)
        except DataEvalError as err:
            msg = "Can't deserialize: %s" % err
            raise forms.ValidationError(msg)


class DictData(dict):
    """
    Can init with a dict:
    >>> DictData({"foo":"bar"}) == {'foo': 'bar'}
    True
    
    Can also init with a string:
    >>> DictData('''{"foo":"bar"}''') == {'foo': 'bar'}
    True
    """
    def __init__(self, value):
        if isinstance(value, six.string_types):
            self.value = value
            super(DictData, self).__init__(data_eval.data_eval(value))
        elif isinstance(value, dict):
            self.value = None
            super(DictData, self).__init__(value)
        else:
            raise TypeError("init data is not from type str/basestring or dict (It's type: %r)" % type(value))

    def __repr__(self):
        """ used in django admin form field and in DictModelField.get_db_prep_save() """
        return pprint.pformat(dict(self))


class DictModelField(models.Field):
    description = "DictModelField"

    """
    A dict field.
    Stores a python dict into a text field.
    
    >>> d=DictModelField().to_python('''{"foo":"bar"}''')
    >>> d == {'foo': 'bar'}
    True
    >>> isinstance(d, DictData)
    True
    >>> DictModelField().get_db_prep_save(d) == "{'foo': 'bar'}"
    True

    >>> f = DictModelField().formfield()
    >>> f.clean('''{"foo":"bar"}''') == {'foo': 'bar'}
    True
    """
    # https://docs.djangoproject.com/en/1.8/releases/1.8/#subfieldbase
    __metaclass__ = models.SubfieldBase # will be removed in Django 2.0

    def get_internal_type(self):
        return "TextField"

    # def __getattribute__(self, item):
    #     print("DictModelField.getattribute:", item)
    #     return super(DictModelField, self).__getattribute__(item)
    #
    # def __getattr__(self, item):
    #     print("DictModelField.getattr:", item)
    #     return super(DictModelField, self).__getattr__(item)
#
    def _check_null(self, value):
        if value is None and self.null == False:
            raise forms.ValidationError(_("This field cannot be null."))
        return value

    def to_python(self, value):
        """
        Converts the input value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.

        to_python() will be not called since 1.8:
        https://docs.djangoproject.com/en/1.8/releases/1.8/#subfieldbase
        """
        value = self._check_null(value)
        if value is None:
            return None

        try:
            return DictData(value)
        except DataEvalError as err:
            msg = "Can't deserialize %r: %s" % (value, err)
            raise forms.ValidationError(msg)

    def from_db_value(self, value, expression=None, connection=None, context=None):
        """
        Converts the input value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.

        from_db_value() is new in new in django 1.8!
        """
        if isinstance(value, dict):
            return value

        value = self._check_null(value)
        if value is None:
            return None

        try:
            return DictData(value)
        except DataEvalError as err:
            msg = "Can't deserialize %r: %s" % (value, err)
            raise forms.ValidationError(msg)

    def get_prep_value(self, value):
        if value:
            return repr(value)
        else:
            return ""

    def get_db_prep_value(self, value, connection, prepared=False):
        "Returns field's value prepared for saving into a database."
        if value:
            return repr(value)
        else:
            return ""

    def formfield(self, **kwargs):
        # Always use own form field and widget:
        kwargs['form_class'] = DictFormField
        return super(DictModelField, self).formfield(**kwargs)


class DictField(object):
    def __new__(cls, *args, **kwargs):
        warnings.warn(
            "You use the old API! DictField was renamed to DictModelField !",
            FutureWarning,
            stacklevel=2
        )
        return DictModelField()


# class DictField(DictModelField):
#     def __new__(cls, *args, **kwargs):
#         warnings.warn(
#             "You use the old API! DictField was renamed to DictModelField !",
#             FutureWarning,
#             stacklevel=2
#         )
#         return DictModelField.__new__(cls, *args, **kwargs)


# class DictField(DictModelField):
#     def __new__(cls, *args, **kwargs):
#         warnings.warn(
#             "You use the old API! DictField was renamed to DictModelField !",
#             FutureWarning,
#             stacklevel=2
#         )
#         return super(DictField, cls).__new__(cls, *args, **kwargs)

