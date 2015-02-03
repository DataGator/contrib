# -*- coding: utf-8 -*-
"""
    tests
    ~~~~~

    Public Test Suite for `DataGator`_.

    .. _`DataGator`: http://www.data-gator.com/

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/01/19
"""

from __future__ import unicode_literals
from .config import to_native

__all__ = ['test_suite', ]
__all__ = [to_native(n) for n in __all__]


import os
import sys

from .config import unittest


from importlib import import_module
from pkgutil import iter_modules


def load_tests(prefix="test_"):
    for _, name, _ in iter_modules([
            os.path.join(".", os.path.dirname(__file__))]):
        if not name.startswith(prefix):
            continue
        mod = import_module(".{0}".format(name), __package__)
        if not callable(getattr(mod, "test_suite", None)):
            continue
        yield mod
    raise StopIteration


def test_suite():
    suite = unittest.TestSuite()
    for pkg in load_tests("test_"):
        suite.addTest(pkg.test_suite())
    return suite
