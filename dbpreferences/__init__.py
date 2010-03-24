# coding:utf-8

""" History: see README """

import os

__version__ = (0, 3, 2)


try:
    from django.utils.version import get_svn_revision
except ImportError:
    pass
else:
    path = os.path.split(os.path.abspath(__file__))[0]
    svn_revision = get_svn_revision(path)
    if svn_revision != u'SVN-unknown':
        svn_revision = svn_revision.replace("-", "").lower()
        __version__ += (svn_revision,)


VERSION_STRING = '.'.join(str(part) for part in __version__)


if __name__ == "__main__":
    print VERSION_STRING
