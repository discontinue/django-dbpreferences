from django.db import models

from dbpreferences.fields import DictModelField

class UnittestDictModelFieldModel(models.Model):
    dict_field = DictModelField()