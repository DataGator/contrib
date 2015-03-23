#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    tests.test_entity
    ~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/03/23
"""

from __future__ import unicode_literals

import json
import jsonschema
import logging
import os
import sys
import time

try:
    from . import config
    from .config import *
except (ValueError, ImportError):
    import config
    from config import *

from datagator.api.client._backend import environ
from datagator.api.client.repo import Repo


__all__ = ['TestRepo',
           ]
__all__ = [to_native(n) for n in __all__]


_log = logging.getLogger("datagator.{0}".format(__name__))


@unittest.skipIf(
    not os.environ.get('DATAGATOR_CREDENTIALS', None) and
    os.environ.get('TRAVIS', False),
    "credentials required for unsupervised testing")
class TestRepo(unittest.TestCase):
    """
    Endpoint:
        ``^/<repo>``
    """

    @classmethod
    def setUpClass(cls):
        environ.DATAGATOR_API_VERSION = "v2"
        cls.repo, cls.secret = get_credentials()
        pass  # void return

    @classmethod
    def tearDownClass(cls):
        pass  # void return

    def test_Repo_GET(self):
        repo = Repo(self.repo)
        self.assertEqual(repo.kind, "Repo")
        self.assertEqual(repo.name, self.repo)
        pass  # void return

    def test_Repo_GET_NonExistence(self):
        r = Repo("NonExistance")
        self.assertRaises(KeyError, len, r)
        pass  # void return

    pass


def test_suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(eval(c)) for c in __all__])


if __name__ == '__main__':
    unittest.main(defaultTest=to_native("test_suite"))
