"""
    unittests for data eval
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the dbpreferences team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import datetime
import unittest


from dbpreferences.tools.data_eval import DataEval, DataEvalError, \
    UnsafeSourceError, EvalSyntaxError


class TestDataEval(unittest.TestCase):
    def literal_eval(self, data_string):
        return DataEval().parse(data_string)

    def assert_eval(self, data):
        data_string = repr(data)
        result = self.literal_eval(data_string)
        self.assertEqual(result, data)

    def test_none(self):
        self.assert_eval(None)

    def test_bool(self):
        self.assert_eval(True)
        self.assert_eval(False)
        self.assert_eval([True, False])
        self.failUnlessEqual(self.literal_eval("true"), True)
        self.failUnlessEqual(self.literal_eval("TRUE"), True)

    def test_const(self):
        self.assert_eval(1)
        self.assert_eval(1.01)
        self.assert_eval("FooBar")
        self.assert_eval(u"FooBar")

    def test_negative_values(self):
        self.assert_eval(-1)
        self.assert_eval(-2.02)

    def test_tuple(self):
        self.assert_eval(())
        self.assert_eval((1, 2))
        self.assert_eval(("1", u"2", None, True, False))

    def test_list(self):
        self.assert_eval([])
        self.assert_eval([1, 2, -3, -4.41])
        self.assert_eval(["foo", u"bar", None, True, False])

    def test_dict(self):
        self.assert_eval({})
        self.assert_eval({1: 2, "a": "b", u"c": "c", "d": -1, "e": -2.02})
        self.assert_eval({"foo": "bar", u"1": None, 1: True, 0: False})

    def test_datetime(self):
        self.assert_eval(datetime.datetime.now())
        self.assert_eval({"dt": datetime.datetime.now()})
        self.assert_eval(datetime.timedelta(seconds=2))

    def test_line_endings(self):
        self.literal_eval("\r\n{\r\n'foo'\r\n:\r\n1\r\n}\r\n")
        self.literal_eval("\r{\r'foo'\r:\r1\r}\r")

    def test_no_string(self):
        self.assertRaises(DataEvalError, self.literal_eval, 1)

    def test_quote_err(self):
        self.assertRaises(UnsafeSourceError, self.literal_eval, "a")
        self.assertRaises(DataEvalError, self.literal_eval, "a")

    def test_unsupported_err(self):
        self.assertRaises(UnsafeSourceError, self.literal_eval, "a+2")
        self.assertRaises(UnsafeSourceError, self.literal_eval, "eval()")
        self.assertRaises(DataEvalError, self.literal_eval, "eval()")

    def test_syntax_error(self):
        self.assertRaises(EvalSyntaxError, self.literal_eval, ":")
        self.assertRaises(EvalSyntaxError, self.literal_eval, "import os")
        self.assertRaises(DataEvalError, self.literal_eval, "import os")


if __name__ == '__main__':
    unittest.main()
