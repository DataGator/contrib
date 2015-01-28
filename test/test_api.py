#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    test.test_api
    ~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/01/19
"""

from __future__ import unicode_literals

__all__ = [b'TestBackendStatus', b'TestRepoOperations', ]


import logging
import os
import sys

from datagator.api import client as api


if os.environ.get("DEBUG", None):
    logging.getLogger().setLevel(logging.DEBUG)

try:
    from . import config
    from .config import unittest, to_native, get_credentials
except (ValueError, ImportError):
    import config
    from config import unittest, to_native, get_credentials


class TestBackendStatus(unittest.TestCase):
    """
    URL Endpoint:
        ``^/``
        ``^/schema``
    """

    @classmethod
    def setUpClass(cls):
        pass  # void return

    def test_backend_status(self):
        pass  # void return

    def test_backend_schema(self):
        pass  # void return

    pass


class TestRepoOperations(unittest.TestCase):
    """

    """

    @classmethod
    def setUpClass(cls):
        pass  # void return

    def test_Repo_GET(self):
        pass  # void return

    @unittest.skipIf(
        not os.environ.get('DATAGATOR_CREDENTIALS', None) and
        os.environ.get('TRAVIS', False),
        "credentials required for unsupervised testing")
    def test_Repo_PUT(self):
        repo, key = get_credentials()
        pass  # void return

    pass


def test_suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(eval(c)) for c in __all__])


if __name__ == '__main__':
    unittest.main(defaultTest=to_native("test_suite"))
