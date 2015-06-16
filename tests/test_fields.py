# coding: utf-8

"""
    DBPreferences - unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the dbpreferences team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function

import unittest
import sys
import django

from django.core.exceptions import ValidationError
from django import forms

from django_tools.unittest_utils.print_sql import PrintQueries

from dbpreferences.fields import DictModelField, DictData, DictFormField

from test_project.models import UnittestDictModelFieldModel


class TestDictFiels(unittest.TestCase):
    def test(self):
        d=DictModelField().to_python('''{"foo":"bar"}''')
        self.assertEqual(d, {'foo': 'bar'})
        self.assertIsInstance(d, DictData)

        s = DictModelField().get_prep_value(d)
        self.assertEqual(s, "{'foo': 'bar'}")

        s = DictModelField().get_db_prep_value(d, connection=None, prepared=False)
        self.assertEqual(s, "{'foo': 'bar'}")

        s = DictModelField().get_db_prep_save(d, connection=None)
        self.assertEqual(s, "{'foo': 'bar'}")

        print("OK")

    def test_not_null(self):
        self.assertRaises(
            ValidationError,
            DictModelField().to_python, None
        )

    def test_clean(self):
        f = DictModelField().formfield()
        d = f.clean('''{"foo":"bar"}''')
        self.assertEqual(d, {'foo': 'bar'})

        self.assertIsInstance(f, DictFormField)


class UnittestDictFormFieldForm(forms.Form):
    dict_field = DictFormField()


class TestDictFormField(unittest.TestCase):
    """
    form field for preferences dict
    """
    def test_form_fiels(self):
        f = DictFormField()
        d = f.clean('''{"foo":"bar"}''')
        self.assertEqual(d, {'foo': 'bar'})

    def test_not_null(self):
        self.assertRaises(
            ValidationError,
            DictFormField().clean, None
        )

    def test_error(self):
        self.assertRaises(
            ValidationError,
            DictFormField().clean, "error"
        )

    def test_form(self):
        form = UnittestDictFormFieldForm({"dict_field": '''{"foo":"bar"}'''})
        self.assertTrue(form.is_valid())
        d = form.cleaned_data["dict_field"]
        self.assertEqual(d, {'foo': 'bar'})



class TestDictModelField(django.test.TestCase):
    def setUp(self):
        self.instance = UnittestDictModelFieldModel.objects.create(
            dict_field = {'foo': 'bar'}
        )
        # XXX: Does this delete the cache really?
        self.query_set = UnittestDictModelFieldModel.objects.get_queryset()
        self.query_set._result_cache = None

    def test_instance(self):
        print(self.instance.dict_field, type(self.instance.dict_field))
        self.assertEqual(self.instance.dict_field, {'foo': 'bar'})
        self.assertEqual(self.instance.pk, 1)
        self.assertEqual(UnittestDictModelFieldModel.objects.count(), 1)

    # def test(self):
    #     with PrintQueries("Change object"):
    #         self.instance.dict_field["new"]=1
    #         self.instance.save()
    #         self.assertEqual(self.instance.dict_field, {'foo': 'bar', "new":1})
    #
    #     with PrintQueries("get object"):
    #         print("\n****UnittestDictModelFieldModel.objects.all()")
    #         query_set = UnittestDictModelFieldModel.objects.filter(pk=self.instance.pk)
    #         print("\n****UnittestDictModelFieldModel.objects.all() done")
    #         # new_instance = query_set[0]
    #         print("\n***get dict_field")
    #         # d = new_instance.dict_field
    #         d = query_set.values("dict_field")
    #         print("\n***repr dict_field 1")
    #         print(repr(d), type(d))
    #         print("\n***repr dict_field 2")
    #         d = d[0]["dict_field"]
    #         print(repr(d), type(d))
    #         self.assertEqual(d, {'foo': 'bar', "new":1})

    def test_get1(self): # FIXME: Will fail with Python 3, but works with Python 2 ?!?
        with self.assertNumQueries(2):
            # with PrintQueries("test_get():"):
            self.instance.dict_field["test"] = "test_get()"
            self.instance.save()

            instance = UnittestDictModelFieldModel.objects.get(pk=1)
            d = instance.dict_field
            self.assertEqual(d, {'foo': 'bar', 'test': 'test_get()'})

    @unittest.expectedFailure # FIXME!
    def test_values(self):
        """
        FIXME: queryset.values() will always return the string and not the dict.

        if .values() used: Theses methods will be not called:

            DictModelField.from_db_value()
            DictModelField.to_python()

        http://www.python-forum.de/viewtopic.php?f=7&t=36503 (de)
        """
        with self.assertNumQueries(2):
            # with PrintQueries("test_values(): 2"):
            values = UnittestDictModelFieldModel.objects.all().values("dict_field")
            d = values[0]["dict_field"]
            self.assertEqual(d, {'foo': 'bar'})

