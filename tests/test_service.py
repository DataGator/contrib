#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    tests.test_service
    ~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/01/19
"""

from __future__ import unicode_literals

try:
    from . import config
    from .config import *
except (ValueError, ImportError):
    import config
    from config import *

__all__ = ['TestBackendStatus',
           'TestRepoOperations',
           'TestDataSetOperations', ]
__all__ = [to_native(n) for n in __all__]


import json
import jsonschema
import logging
import os
import sys
import time

from datagator.api.client._backend import environ, DataGatorService


_log = logging.getLogger("datagator.{0}".format(__name__))


def monitor_task(service, url, retry=5):
    task = None
    while retry > 0:
        task = service.http.get(url).json()
        assert(task.get("kind") == "datagator#Task")
        if task.get("status") in ("SUC", "ERR"):
            break
        time.sleep(0.5)
        retry -= 1
    return task


class TestBackendStatus(unittest.TestCase):
    """
    Endpoint:
        ``^/``
        ``^/schema``
    """

    @classmethod
    def setUpClass(cls):
        cls.service = DataGatorService()
        pass  # void return

    @classmethod
    def tearDownClass(cls):
        del cls.service
        pass  # void return

    def test_backend_status(self):
        msg = self.service.status
        validator = jsonschema.Draft4Validator(self.service.schema)
        self.assertEqual(validator.validate(msg), None)
        self.assertEqual(msg.get("kind"), "datagator#Status")
        self.assertEqual(msg.get("code"), 200)
        self.assertEqual(msg.get("version"), environ.DATAGATOR_API_VERSION)
        pass  # void return

    pass


@unittest.skipIf(
    not os.environ.get('DATAGATOR_CREDENTIALS', None) and
    os.environ.get('TRAVIS', False),
    "credentials required for unsupervised testing")
class TestRepoOperations(unittest.TestCase):
    """
    Endpoint:
        ``^/<repo>``
    """

    @classmethod
    def setUpClass(cls):
        cls.repo, cls.secret = get_credentials()
        cls.service = DataGatorService(auth=(cls.repo, cls.secret))
        cls.validator = jsonschema.Draft4Validator(cls.service.schema)
        pass  # void return

    @classmethod
    def tearDownClass(cls):
        del cls.service
        pass  # void return

    def test_Repo_GET(self):
        repo = self.service.get(self.repo).json()
        self.assertEqual(self.validator.validate(repo), None)
        self.assertEqual(repo.get("kind"), "datagator#Repo")
        self.assertEqual(repo.get("name"), self.repo)
        pass  # void return

    def test_Repo_GET_NonExistence(self):
        msg = self.service.get("NonExistence").json()
        self.assertEqual(self.validator.validate(msg), None)
        self.assertEqual(msg.get("kind"), "datagator#Error")
        self.assertEqual(msg.get("code"), 404)
        pass  # void return

    def test_Repo_PUT(self):

        IGO_Members = {
            "kind": "datagator#DataSet",
            "name": "IGO_Members",
            "repo": {
                "kind": "datagator#Repo",
                "name": self.repo
            }
        }

        response = self.service.put(self.repo, IGO_Members)
        msg = response.json()
        self.assertEqual(self.validator.validate(msg), None)
        _log.debug(msg.get("message"))
        self.assertEqual(msg.get("kind"), "datagator#Status")
        self.assertEqual(msg.get("code"), 202)

        # monitor the task until the data set is ready or an error occurs
        self.assertTrue("Location" in response.headers)
        url = response.headers['Location']
        task = monitor_task(self.service, url)
        self.assertEqual(self.validator.validate(task), None)
        self.assertEqual(task.get("kind"), "datagator#Task")
        self.assertEqual(task.get("status"), "SUC")

        # commit an initial revision to the created data set
        UN = json.loads(to_unicode(
            load_data(os.path.join("json", "IGO_Members", "UN.json"))))
        response = self.service.put(
            "{0}/{1}".format(self.repo, "IGO_Members"), {"UN": UN})
        msg = response.json()
        self.assertEqual(self.validator.validate(msg), None)
        _log.debug(msg.get("message"))
        self.assertEqual(msg.get("kind"), "datagator#Status")
        self.assertEqual(msg.get("code"), 202)

        # monitor the task until the revision is committed an error occurs
        self.assertTrue("Location" in response.headers)
        url = response.headers['Location']
        task = monitor_task(self.service, url)
        self.assertEqual(self.validator.validate(task), None)
        self.assertEqual(task.get("kind"), "datagator#Task")
        self.assertEqual(task.get("status"), "SUC")

        pass  # void return

    pass


@unittest.skipIf(
    not os.environ.get('DATAGATOR_CREDENTIALS', None) and
    os.environ.get('TRAVIS', False),
    "credentials required for unsupervised testing")
class TestDataSetOperations(unittest.TestCase):
    """
    Endpoint:
        ``^/<repo>``
    """

    @classmethod
    def setUpClass(cls):
        cls.repo, cls.secret = get_credentials()
        cls.service = DataGatorService(auth=(cls.repo, cls.secret))
        cls.validator = jsonschema.Draft4Validator(cls.service.schema)
        pass  # void return

    @classmethod
    def tearDownClass(cls):
        del cls.service
        pass  # void return

    def test_DataSet_GET(self):
        response = self.service.get("{0}/{1}".format(self.repo, "IGO_Members"))
        ds = response.json()
        self.assertEqual(self.validator.validate(ds), None)
        self.assertEqual(ds.get("kind"), "datagator#DataSet")
        self.assertEqual(ds.get("name"), "IGO_Members")

        # check if ds/repo/name matches the requested one
        repo = ds.get("repo")
        self.assertEqual(self.validator.validate(repo), None)
        self.assertEqual(repo.get("kind"), "datagator#Repo")
        self.assertEqual(repo.get("name"), self.repo)

        pass  # void return

    def test_DataSet_GET_NonExistence(self):
        msg = self.service.get("Pardee/NonExistence").json()
        self.assertEqual(self.validator.validate(msg), None)
        self.assertEqual(msg.get("kind"), "datagator#Error")
        self.assertEqual(msg.get("code"), 404)
        pass  # void return

    def test_DataSet_PUT(self):

        revisions = {
            "WTO": json.loads(to_unicode(
                load_data(os.path.join("json", "IGO_Members", "WTO.json")))),
            "IMF": json.loads(to_unicode(
                load_data(os.path.join("json", "IGO_Members", "IMF.json")))),
            "OPEC": json.loads(to_unicode(
                load_data(os.path.join("json", "IGO_Members", "OPEC.json")))),
        }

        response = self.service.put(
            "{0}/{1}".format(self.repo, "IGO_Members"), revisions)
        msg = response.json()
        self.assertEqual(self.validator.validate(msg), None)
        _log.debug(msg.get("message"))
        self.assertEqual(msg.get("kind"), "datagator#Status")
        self.assertEqual(msg.get("code"), 202)

        # monitor the task until the revision is committed an error occurs
        self.assertTrue("Location" in response.headers)
        url = response.headers['Location']
        task = monitor_task(self.service, url)
        self.assertEqual(self.validator.validate(task), None)
        self.assertEqual(task.get("kind"), "datagator#Task")
        self.assertEqual(task.get("status"), "SUC")

        pass  # void return

    pass


def test_suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(eval(c)) for c in __all__])


if __name__ == '__main__':
    unittest.main(defaultTest=to_native("test_suite"))
