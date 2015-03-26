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

from datagator.api.client import environ
from datagator.api.client import Repo, DataSet


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

    def test_Repo_init(self):
        repo = Repo(self.repo)
        self.assertEqual(repo.kind, "Repo")
        self.assertEqual(repo.name, self.repo)
        pass  # void return

    def test_Repo_init_NonExistence(self):
        self.assertRaises((AssertionError, RuntimeError), Repo, "NonExistence")
        pass  # void return

    def test_Repo_contains(self):
        repo = Repo(self.repo)
        self.assertTrue("IGO_Members" in repo)
        self.assertTrue("NonExistence" not in repo)
        self.assertTrue("A#B" not in repo)
        pass  # void return

    def test_Repo_iter(self):
        repo = Repo(self.repo)
        cnt = 0
        for dsname in repo:
            cnt += 1
        self.assertEqual(len(repo), cnt)
        pass  # void return

    def test_Repo_item(self):
        repo = Repo(self.repo, self.secret)
        repo['IGO_Members'] = []
        self.assertIsInstance(repo['IGO_Members'], DataSet)
        pass  # void return

    pass


def test_suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(eval(c)) for c in __all__])


if __name__ == '__main__':
    unittest.main(defaultTest=to_native("test_suite"))
