import unittest
from dbpreferences.fields import DictModelField, DictData, DictFormField
from django.core.exceptions import ValidationError


class TestDictFiels(unittest.TestCase):
    def test(self):
        d=DictModelField().to_python('''{"foo":"bar"}''')
        self.assertEqual(d, {'foo': 'bar'})
        self.assertIsInstance(d, DictData)

        s = DictModelField().get_db_prep_save(d)
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