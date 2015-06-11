# -*- coding: utf-8 -*-
"""
    some utils around newforms
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2008-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest

from django import forms
from django.forms import ValidationError
from django.utils import six
from django.utils.encoding import smart_text, force_text
from django.utils.html import escape


def setup_help_text(form):
    """
    Append on every help_text the default information (The initial value)
    """
    for field_name, field in form.base_fields.items():
        help_text = six.text_type(field.help_text) # translate gettext_lazy
        if u"(default: '" in help_text:
            # The default information was inserted in the past
            return
        initial_text = escape(force_text(field.initial))
        field.help_text = u"%s (default: '%s')" % (
            field.help_text, initial_text
        )

def get_init_dict(form):
    """
    Returns a dict with all initial values from a newforms class.
    """
    init_dict = {}
    for field_name, field in form.base_fields.items():
        initial = field.initial
#        if initial == None:
#            msg = (
#                "The preferences model attribute '%s' has no initial value!"
#            ) % field_name
#            raise NoInitialError(msg)

        init_dict[field_name] = initial
    return init_dict


class NoInitialError(Exception):
    """
    All preferences newform attributes must habe a initial value.
    """
    pass


class ChoiceField2(forms.ChoiceField):
    """
    Works like a ChoiceField, but accepts a list of items. The list are
    converted to a tuple fpr rendering.
    Returns the value and not the key in clean().

    >>> f = ChoiceField2(choices=["A","B","C"])
    >>> f.choices == [('0', 'A'), ('1', 'B'), ('2', 'C')]
    True
    >>> f.clean('1') == 'B'
    True
    """
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop("choices")
        kwargs["choices"] = self.choices = [
            (str(no), smart_text(value)) for no, value in enumerate(choices)
        ]

        super(ChoiceField2, self).__init__(*args, **kwargs)

    def clean(self, value):
        """
        Validates that the input and returns the choiced value.
        """
        key = super(ChoiceField2, self).clean(value)
        choices_dict = dict(self.choices)
        return choices_dict[key]


class StripedCharField(forms.CharField):
    """
    Same as forms.CharField but stripes the output.

    >>> f = StripedCharField()
    >>> f.clean('\\n\\n[\\nTEST\\n]\\n\\n') == '[\\nTEST\\n]'
    True
    """
    def clean(self, value):
        value = super(StripedCharField, self).clean(value)
        return value.strip()


class ListCharField(forms.CharField):
    """
    Items seperated by spaces or other characters.
    If the initial is a list/tuple, it would be joined with the seperator.

    >>> f = ListCharField()
    >>> f.clean(' one two  tree') == ['one', 'two', 'tree']
    True

    >>> f = ListCharField(seperator="\\n")
    >>> f.clean('one\\ntwo\\n\\ntree\\n\\n') == ['one', 'two', 'tree']
    True
    """
    def __init__(self, seperator=" ", *args, **kwargs):
        self.seperator = seperator
        if "initial" in kwargs:
            initial = kwargs["initial"]
            if isinstance(initial, (list, tuple)):
                kwargs["initial"] = self.seperator.join(initial)
        super(ListCharField, self).__init__(*args, **kwargs)

    def clean(self, value):
        raw_value = super(ListCharField, self).clean(value)
        value = raw_value.strip()
        items = [i.strip() for i in value.split(self.seperator)]
        items = [i for i in items if i] # eliminate empty items
        return items

class ListCharFieldTest(unittest.TestCase):
    def test(self):
        """ Test if a give list would be joined with the seperator"""
        class TestForm(forms.Form):
            foo = ListCharField(
                seperator="\n", initial=[u'one', u'two', u'tree']
            )

        f = TestForm()
        self.failUnlessEqual(
            f.as_p(),
            '<p><label for="id_foo">Foo:</label> '
            '<input type="text" name="foo" value="one\ntwo\ntree" id="id_foo" />'
            '</p>'
        )

class InternalURLField(forms.CharField):
    """
    Uses e.g. for back urls via a http GET parameter
    validates the URL and check if is't a internal url and not
    a external.

    >>> f = InternalURLField()
    >>> f.clean('/a/foobar/url/') == '/a/foobar/url/'
    True

    >>> try:
    ...     f.clean('http://eval.domain.tld')
    ... except ValidationError as err:
    ...     err.message == 'Open redirect found.'
    True

    >>> f = InternalURLField(must_start_with="/_command/")
    >>> f.clean('/_command/a/foobar/url/') == '/_command/a/foobar/url/'
    True

    >>> try:
    ...     f.clean('/a/wrong/url/')
    ... except ValidationError as err:
    ...     err.message == 'Open redirect found.'
    True
    """
    default_error_message = "Open redirect found."

    def __init__(self, must_start_with=None, *args, **kwargs):
        self.must_start_with = must_start_with
        super(InternalURLField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(InternalURLField, self).clean(value)
        if "://" in value:
            raise ValidationError(self.default_error_message)
        if self.must_start_with and not value.startswith(self.must_start_with):
            raise ValidationError(self.default_error_message)
        return value


class ModelForm2(forms.ModelForm):
    """
    A model form witch don't validate unique fields.

    This ModelForm is only for generating the forms and not for create/update
    any database data. So a field unique Test would like generate Errors like:
        User with this Username already exists.

    see also:
    http://www.jensdiemer.de/_command/118/blog/detail/30/ (de)
    http://www.python-forum.de/topic-16000.html (de)
    """
    def validate_unique(self):
        pass




if __name__ == "__main__":
    import doctest
    doctest.testmod(
        verbose=False
    )
    print("DocTest end.")

    unittest.main()
