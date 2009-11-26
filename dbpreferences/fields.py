# coding: utf-8

"""
    DBPreferences - fields
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
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group

from dbpreferences.tools import forms_utils, easy_import, data_eval
from dbpreferences.tools.data_eval import DataEvalError



class DictFormField(forms.CharField):
    """
    form field for preferences dict
    
    >>> DictFormField().clean('''{"foo":"bar"}''')
    {'foo': 'bar'}
    
    >>> DictFormField().clean("error")
    Traceback (most recent call last):
        ...
    ValidationError: [u"Can't deserialize: Error 'Strings must be quoted' in line 1: 'error'"]
    
    >>> DictFormField().clean(None)
    Traceback (most recent call last):
        ...
    ValidationError: [u'This field is required.']
    
    >>> DictFormField(required=False).clean(None)
    u''
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
        except DataEvalError, err:
            msg = "Can't deserialize: %s" % err
#            msg = "Can't deserialize %r: %s" % (value, err)
            raise forms.ValidationError(msg)


class DictData(dict):
    """
    Can init with a dict:
    >>> DictData({"foo":"bar"})
    {'foo': 'bar'}
    
    Can also init with a string:
    >>> DictData('''{"foo":"bar"}''')
    {'foo': 'bar'}
    """
    def __init__(self, value):
        if isinstance(value, basestring):
            self.value = value
            super(DictData, self).__init__(data_eval.data_eval(value))
        elif isinstance(value, dict):
            self.value = None
            super(DictData, self).__init__(value)
        else:
            raise TypeError("init data is not from type basestring or dict (It's type: %r)" % type(value))

    def __repr__(self):
        """ used in django admin form field and in DictField.get_db_prep_save() """
        return pprint.pformat(dict(self))


class DictField(models.TextField):
    """
    A dict field.
    Stores a python dict into a text field.
    
    >>> d = DictField().to_python('''{"foo":"bar"}''')
    >>> d
    {'foo': 'bar'}
    >>> isinstance(d, DictData)
    True
    >>> DictField().get_db_prep_save(d)
    "{'foo': 'bar'}"
    
    >>> d = DictField().to_python(None)
    Traceback (most recent call last):
        ...
    ValidationError: [u'This field cannot be null.']
    
    >>> f = DictField().formfield()
    >>> isinstance(f, DictFormField)
    True
    >>> f.clean('''{"foo":"bar"}''')
    {'foo': 'bar'}
    """
    __metaclass__ = models.SubfieldBase

    def _check_null(self, value):
        if value is None and self.null == False:
            raise forms.ValidationError(_("This field cannot be null."))
        return value

    def to_python(self, value):
        """
        Converts the input value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        value = self._check_null(value)
        if value is None:
            return None

        try:
            return DictData(value)
        except DataEvalError, err:
#            msg = "Can't deserialize: %s" % err
            msg = "Can't deserialize %r: %s" % (value, err)
            raise forms.ValidationError(msg)

    def get_db_prep_save(self, value):
        "Returns field's value prepared for saving into a database."
        value = self._check_null(value)
        if value is None:
            return None

        assert isinstance(value, (DictData, dict))
        return repr(value)
#
    def formfield(self, **kwargs):
        # Always use own form field and widget:
        kwargs['form_class'] = DictFormField
        return super(DictField, self).formfield(**kwargs)



if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
