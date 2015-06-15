"""
    Data eval
    ~~~~~~~~~

    Evaluate a Python expression string, but only Python data type objects:
        - Constants, Dicts, Lists, Tuples
        - from datetime: datetime and timedelta

    Error class hierarchy:

        DataEvalError
         +-- EvalSyntaxError (compiler SyntaxError)
         +-- UnsafeSourceError (errors from the AST walker)

    A full featured "safe data eval" can be found here:
        https://github.com/newville/asteval/

    :copyleft: 2008-2015 by the dbpreferences team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import ast
import datetime

from django.utils import six

NAME_MAP = {"none": None, "true": True, "false": False}


if six.PY2:
    AST_TEXT_NODES = ast.Str
else:
    AST_TEXT_NODES = (ast.Str, ast.Bytes)


def pprint_node(node):
    for attr in dir(node):
        print(attr, getattr(node, attr, "-"))


class DataEvalError(Exception):
    """ main error class for all data eval errors """
    pass


class EvalSyntaxError(DataEvalError):
    """ compile raised a SyntaxError"""
    pass


class UnsafeSourceError(DataEvalError):
    """ Error class for the SafeEval AST walker """
    pass


class DataEval(object):
    def convert(self, node):
        if isinstance(node, ast.Expression):
            node = node.body

        if isinstance(node, AST_TEXT_NODES):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Tuple):
            return tuple(map(self.convert, node.elts))
        elif isinstance(node, ast.List):
            return list(map(self.convert, node.elts))
        elif isinstance(node, ast.Set):
            return set(map(self.convert, node.elts))
        elif isinstance(node, ast.Dict):
            return dict((self.convert(k), self.convert(v)) for k, v
                in zip(node.keys, node.values))
        elif not six.PY2 and isinstance(node, ast.NameConstant):
            # ast.NameConstant exists only in Py3 !
            return node.value
        elif isinstance(node, ast.UnaryOp) and \
                isinstance(node.op, (ast.UAdd, ast.USub)) and \
                isinstance(node.operand, (ast.Num, ast.UnaryOp, ast.BinOp)):
            operand = self.convert(node.operand)
            if isinstance(node.op, ast.UAdd):
                return + operand
            else:
                return - operand
        elif isinstance(node, ast.BinOp) and \
                isinstance(node.op, (ast.Add, ast.Sub)) and \
                isinstance(node.right, (ast.Num, ast.UnaryOp, ast.BinOp)) and \
                isinstance(node.left, (ast.Num, ast.UnaryOp, ast.BinOp)):
            left = self.convert(node.left)
            right = self.convert(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            else:
                return left - right
        elif isinstance(node, ast.Call):
            return self._call(node)
        elif isinstance(node, ast.Name):
            key = node.id
            key = key.lower()
            try:
                return NAME_MAP[key]
            except KeyError as err:
                raise UnsafeSourceError("Name '%s' not supported." % node.id)

        raise UnsafeSourceError(
            "malformed node or string! repr: %r - dump %s" % (
                repr(node), ast.dump(node)
            )
        )

    def _call(self, node):
        try:
            callable_name = node.func.attr
        except AttributeError as err:
            raise UnsafeSourceError(err)

        callable_name = callable_name.lower()

        method_name = "call_%s" % callable_name
        func = getattr(self, method_name, None)
        if func is None:
            raise ValueError("Func '%s' not exists for node: %s" % (
                method_name, repr(node)
            ))
        return func(node)

    def call_datetime(self, node):
        args = list(map(self.convert, node.args))
        return datetime.datetime(*args)

    def call_timedelta(self, node):
        args = list(map(self.convert, node.args))
        return datetime.timedelta(*args)

    def parse(self, source):
        if isinstance(source, dict):
            return source
        elif not isinstance(source, six.string_types):
            raise DataEvalError(
                "source must be string/unicode! (It's type: %r)" % type(source))

        try:
            node = ast.parse(source, mode='eval')
        except SyntaxError as err:
            raise EvalSyntaxError(err)
        except Exception as err:
            raise DataEvalError(err)
        return self.convert(node)


def data_eval(data_string):
    return DataEval().parse(data_string)


if __name__ == '__main__':
    def test(data):
        print("-" * 79)
        data_string = repr(data)
        print(data_string)
        data = DataEval().parse(data_string)
        print(repr(data))
        print("-" * 79)

    print(test("a=1"))
    print(test("foo='bar'"))

    test(datetime.datetime.now())
    test({"dt": datetime.datetime.now()})
    test(datetime.timedelta(seconds=2))
