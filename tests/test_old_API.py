import unittest

from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer


class TestOldAPI(unittest.TestCase):
    def test_dict_field(self):
        with StdoutStderrBuffer() as buffer:
            from dbpreferences.fields import DictField
            DictField()

        output = buffer.get_output()
        # print("\n\n*****", output)
        self.assertIn(
            "FutureWarning: You use the old API! DictField was renamed to DictModelField !",
            output
        )