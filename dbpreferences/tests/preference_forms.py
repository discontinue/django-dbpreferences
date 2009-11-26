#coding:utf-8

from django import forms

from dbpreferences.forms import DBPreferencesBaseForm
from dbpreferences.models import Preference

class UnittestForm(DBPreferencesBaseForm):
    """ preferences test form for the unittest """
    subject = forms.CharField(initial="foobar", help_text="Some foo text")
    foo_bool = forms.BooleanField(initial=True, required=False, help_text="Yes or No?")
    count = forms.IntegerField(initial=10, min_value=1, help_text="A max number")
    font_size = forms.FloatField(initial=0.7, min_value=0.1, help_text="font size")

    class Meta:
        app_label = 'dbpreferences.tests'


class TestModelChoiceForm(DBPreferencesBaseForm):
    model_choice = forms.ModelChoiceField(
        queryset=Preference.objects.all(), empty_label=None,
        required=False, initial=None,
    )

    class Meta:
        app_label = 'dbpreferences.tests'
