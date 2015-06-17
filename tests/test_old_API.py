import unittest
import warnings


class TestOldAPI(unittest.TestCase):
    def test_dict_field(self):
        with warnings.catch_warnings(record=True) as warns:
            warnings.simplefilter('always') # prevent warnings from appearing as errors

            from dbpreferences.fields import DictField
            DictField()

            self.assertEqual(len(warns), 1)
            msg = str(warns[0].message)
            self.assertEqual(msg,
                "You use the old API! DictField was renamed to DictModelField !"
            )