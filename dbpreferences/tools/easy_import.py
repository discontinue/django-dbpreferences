# -*- coding: utf-8 -*-

"""
    Import2
    ~~~~~~~

    a easy to use __import__

    TODO: Check import helper in django !

    :copyleft: 2008-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.utils import six


def import2(from_name, fromlist=None, globals={}, locals={}):
    """
    A easy __import__ function.
    TODO: Python 2.5 level argument not supported, yet.
    Link: http://www.python-forum.de/topic-14591.html (de)

    >>> import sys
    >>> sys2 = import2("sys")
    >>> sys is sys2
    True

    >>> from time import time
    >>> time2 = import2("time", "time")
    >>> time is time2
    True

    >>> from os.path import sep
    >>> sep2 = import2("os.path", "sep")
    >>> sep is sep2
    True

    >>> from os import sep, pathsep
    >>> sep2, pathsep2 = import2("os", ["sep", "pathsep"])
    >>> sep is sep2 and pathsep is pathsep2
    True

    >>> try:
    ...     import2("doesnentexisst")
    ... except ImportError as err:
    ...     if six.PY3:
    ...         err.args == ("No module named 'doesnentexisst'",)
    ...     else:
    ...         err.args == ("No module named doesnentexisst",)
    True

    >>> try:
    ...     import2("os", "doesnentexisst")
    ... except AttributeError as err:
    ...     err.args == ("'os' object has no attribute 'doesnentexisst",)
    True
    """

    if isinstance(fromlist, six.string_types):
        # Only one from objects name
        fromlist = [fromlist]

    obj = __import__(from_name, globals, locals, fromlist)
    if fromlist==None:
        # Without a fromlist
        return obj

    # get all 'fromlist' objects
    result = []
    for object_name in fromlist:
        try:
            result.append(getattr(obj, object_name))
        except AttributeError as e:
            msg = "'%s' object has no attribute '%s" % (
                obj.__name__, object_name
            )
            raise AttributeError(msg)

    if len(result) == 1:
        return result[0]
    else:
        return result


def import3(from_name, object_name):
    """
    Thin layer aroung import2():
      - other error handling: raise original error or always a ImportError
      - catch SyntaxError, too (e.g. developing a PyLucid plugin)
      - convert unicode to string (Names from database are always unicode and
        the __import__ function must get strings)

    >>> from time import time
    >>> time2 = import3(u"time", u"time")
    >>> time is time2
    True

    >>> try:
    ...     import3(u"A", u"B")
    ... except ImportError as err:
    ...     if six.PY3:
    ...         err.args == ("Can't import 'B' from 'A': No module named 'A'",)
    ...     else:
    ...         err.args == ("Can't import 'B' from 'A': No module named A",)
    True
    """
    try:
        # unicode -> string
        from_name = str(from_name)
        object_name = str(object_name)

        return import2(from_name, object_name)
    except (ImportError, SyntaxError) as err:
        raise ImportError("Can't import '%s' from '%s': %s" % (
            object_name, from_name, err
        ))


