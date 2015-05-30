#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    tests.test_url_routing
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/05/30
"""

from __future__ import unicode_literals

import json
import jsonschema
import logging
import os
import requests
import sys
import time

try:
    from . import config
    from .config import *
except (ValueError, ImportError):
    import config
    from config import *

from datagator.api.client import environ
from datagator.api.client._backend import DataGatorService


__all__ = ['TestUrlRouting', ]
__all__ = [to_native(n) for n in __all__]


_log = logging.getLogger("datagator.{0}".format(__name__))


class TestUrlRouting(unittest.TestCase):
    """
    Tests the correct routing of full-site URL's.
    """

    @classmethod
    def setUpClass(cls):
        pass  # void return

    @classmethod
    def tearDownClass(cls):
        pass  # void return

    def test_http_to_https_redirect(self):
        uri = "http://{0}/api/v2/".format(environ.DATAGATOR_API_HOST)
        r = requests.get(uri)
        self.assertTrue(len(r.history))
        r0 = r.history[0]
        self.assertEqual(r0.status_code, 302)
        pass  # void return

    def test_admin_redirect(self):
        uri = "{0}://{1}/admin".format(
            environ.DATAGATOR_API_SCHEME,
            environ.DATAGATOR_API_HOST)
        r = requests.get(uri)
        self.assertTrue(r.headers['Content-Type'].startswith("text/html"))
        self.assertTrue(len(r.history))
        r0 = r.history[0]
        self.assertEqual(r0.status_code, 302)
        pass  # void return

    def test_api_v1_root_redirect(self):
        environ.DATAGATOR_API_VERSION = "v1"
        uri = "{0}".format(environ.DATAGATOR_API_URL)
        r = requests.get(uri)
        self.assertEqual(r.headers['Content-Type'], "application/json")
        self.assertTrue(len(r.history))
        r0 = r.history[0]
        self.assertEqual(r0.status_code, 302)
        pass  # void return

    def test_api_v2_root_redirect(self):
        environ.DATAGATOR_API_VERSION = "v2"
        uri = "{0}".format(environ.DATAGATOR_API_URL)
        r = requests.get(uri)
        self.assertEqual(r.headers['Content-Type'], "application/json")
        self.assertTrue(len(r.history))
        r0 = r.history[0]
        self.assertEqual(r0.status_code, 302)
        pass  # void return

    def test_api_v2_non_service(self):
        environ.DATAGATOR_API_VERSION = "v2"
        uri = "{0}/not-a-service".format(environ.DATAGATOR_API_URL)
        r = requests.get(uri)
        self.assertEqual(r.headers['Content-Type'], "application/json")
        msg = r.json()
        self.assertEqual(msg['kind'], "datagator#Error")
        self.assertEqual(msg['message'], "Service not found.")
        pass  # void return

    pass


def test_suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(eval(c)) for c in __all__])


if __name__ == '__main__':
    unittest.main(defaultTest=to_native("test_suite"))
