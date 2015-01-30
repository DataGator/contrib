#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    test.test_api
    ~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Creative Commons 4.0 License (`CC BY-NC-SA 4.0`_).

    .. _`CC BY-NC-SA 4.0`: http://creativecommons.org/licenses/by-nc-sa/4.0/

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/01/19
"""

from __future__ import unicode_literals

__all__ = [b'TestBackendStatus', ]


import logging
import os
import sys

from datagator.api import client as api


if os.environ.get("DEBUG", None):
    logging.getLogger().setLevel(logging.DEBUG)

try:
    from . import config
    from .config import unittest, to_native
except (ValueError, ImportError):
    import config
    from config import unittest, to_native


class TestBackendStatus(unittest.TestCase):
    """
    URL Endpoint:
        ``^/``
        ``^/schema``
    """

    @classmethod
    def setUpClass(cls):
        pass  # void return

    def test_api_status(self):
        pass  # void return

    def test_api_schema(self):
        pass  # void return

    pass


def test_suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(eval(c)) for c in __all__])


if __name__ == '__main__':
    unittest.main(defaultTest=to_native("test_suite"))
