# coding: utf-8

"""
    DBPreferences - fields
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2011 by the dbpreferences team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function

import warnings

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
        if isinstance(value, dict):
            super(DictData, self).__init__(value)
        else:
            d = data_eval.data_eval(value)
            assert isinstance(d, dict)
            super(DictData, self).__init__(d)

        # if isinstance(value, six.string_types):
        #     self.value = value
        #     super(DictData, self).__init__()
        # elif isinstance(value, dict):
        #     self.value = None
        #     super(DictData, self).__init__(value)
        # else:
        #     raise TypeError("init data is not from type str/basestring or dict (It's type: %r)" % type(value))

    def __repr__(self):
        """ used in django admin form field and in DictModelField.get_db_prep_save() """
        return pprint.pformat(dict(self))


# https://docs.djangoproject.com/en/1.8/releases/1.8/#subfieldbase
@six.add_metaclass(models.SubfieldBase) # SubfieldBase will be removed in Django 2.0
class DictModelField(models.Field):
    description = "DictModelField"

    """
    A dict field.
    Stores a python dict into a text field.

    https://docs.djangoproject.com/en/1.8/howto/custom-model-fields/#converting-values-to-python-objects
    
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

    def get_internal_type(self):
        return "TextField"

    # def __getattribute__(self, item):
    #     result = super(DictModelField, self).__getattribute__(item)
    #     print("DictModelField.getattribute: %20s: %r" % (item, result))
    #     return result
    #
    # def __getattr__(self, item):
    #     result = super(DictModelField, self).__getattr__(item)
    #     print("DictModelField.getattr: %20s: %r" % (item, result))
    #     return result

    def to_python(self, value):
        """
        Converts the input value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.

        to_python() will be not called since 1.8:
        https://docs.djangoproject.com/en/1.8/releases/1.8/#subfieldbase
        """
        result = self.from_db_value(value)
        print("\nDictModelField.to_python() return", result, type(result))
        return result

    def from_db_value(self, value, expression=None, connection=None, context=None):
        """
        Converts the input value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.

        from_db_value() is new in new in django 1.8!
        """
        # print("\nDictModelField.from_db_value()")
        if isinstance(value, dict):
            # print("is a dict")
            return value

        if value is None:
            if self.null == False:
                raise forms.ValidationError(_("This field cannot be null."))
            else:
                # print("is None")
                return None

        try:
            result = DictData(value)
            # print("\nDictModelField.from_db_value() return", result, type(result))
            return result
        except DataEvalError as err:
            msg = "Can't deserialize %r: %s" % (value, err)
            raise forms.ValidationError(msg)

    def get_prep_value(self, value):
        """
        Perform preliminary non-db specific value checks and conversions.
        """
        if value is not None:
            return repr(value)
        else:
            if self.null == False:
                raise forms.ValidationError(_("This field cannot be null."))
            else:
                return None

    def formfield(self, **kwargs):
        # Always use own form field and widget:
        kwargs['form_class'] = DictFormField
        return super(DictModelField, self).formfield(**kwargs)


def DictField(*args, **kwargs):
    "TODO: remove this old API support in future!"
    warnings.warn(
        "You use the old API! DictField was renamed to DictModelField !",
        FutureWarning,
        stacklevel=2
    )
    return DictModelField(*args, **kwargs)
