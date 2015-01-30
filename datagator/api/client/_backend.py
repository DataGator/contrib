# -*- coding: utf-8 -*-
"""
    datagator.api.client._backend
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/01/28
"""

from __future__ import unicode_literals, with_statement

__all__ = [b'DATAGATOR_API_USER_AGENT',
           b'DATAGATOR_API_URL',
           b'DATAGATOR_API_FOLLOW_REDIRECT',
           b'DATAGATOR_API_TIMEOUT',
           b'DATAGATOR_API_ACCEPT_ENCODING',
           b'DataGatorClient']


import json
import jsonschema
import requests

from . import __version__ as __client_version__
from ._compat import to_bytes


DATAGATOR_API_USER_AGENT = "datagator-client " \
                           "(python/{0}.{1}.{2})".format(*__client_version__)

DATAGATOR_API_URL = "https://www.data-gator.com/api/v1"
DATAGATOR_API_FOLLOW_REDIRECT = False
DATAGATOR_API_TIMEOUT = 180

DATAGATOR_API_ACCEPT_ENCODING = "gzip, deflate, identity"


class DataGatorClient(object):

    __slots__ = ['__http', ]

    def __init__(self, auth=None):
        self.__http = requests.Session()
        self.http.headers.update({
            "User-Agent": DATAGATOR_API_USER_AGENT,
            "Accept-Encoding": DATAGATOR_API_ACCEPT_ENCODING,
            "Content-Type": "application/json"})
        self.http.auth = auth
        pass

    @property
    def http(self):
        return self.__http

    pass


def commit(dataset, changes, **kwargs):
    """
    :param dataset: identifier of the targeted ``DataSet``
    :param changes: ``dict`` of commit operations
    """

    # HTTP(S) session
    s = DataGatorSession(auth=(kwargs['user'], kwargs['password']))

    # HTTP(S) POST request
    payload = to_bytes(json.dumps(changes))

    r = None
    try:
        r = s.http.request(
            method="PUT",
            url="/".join([DATAGATOR_API_URL, dataset]),
            verify=True,
            data=payload,
            headers=headers,
            allow_redirects=DATAGATOR_API_FOLLOW_REDIRECT,
            timeout=DATAGATOR_API_TIMEOUT)
    except:
        raise
    else:
        return r
    finally:
        s.http.close()

    pass  # void return
