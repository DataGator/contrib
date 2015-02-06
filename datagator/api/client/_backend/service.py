# -*- coding: utf-8 -*-
"""
    datagator.api.client._backend.service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/01/28
"""

from __future__ import unicode_literals, with_statement
from .._compat import to_native

__all__ = ['DataGatorService', ]
__all__ = [to_native(n) for n in __all__]


import json
import logging
import os
import requests

from . import environ
from .._compat import to_bytes

_log = logging.getLogger("datagator.api.client")


class DataGatorService(object):
    """
    HTTP client for DataGator's backend services.
    """

    __slots__ = ['__http', '__auth', ]

    def __init__(self, auth=None, verify=not environ.DEBUG):
        """
        Optional arguments:

        :param auth: 2-``tuple`` of ``<username>`` and ``<secret>`` for use
            in HTTP basic authentication, defaults to ``None``.
        :param verify: perform SSL verification, defaults to ``False`` in
            debugging mode and ``True`` otherwise.
        """

        self.__http = requests.Session()

        if auth:
            _log.info("enabled HTTP authentication")
            self.__auth = auth
        else:
            self.__auth = None

        # turn off SSL verification in DEBUG mode, i.e. the testbed web server
        # may not have a domain name matching the official SSL certificate
        if verify:
            self.http.verify = verify
        else:
            _log.warning("disabled SSL verification")
            self.http.verify = False

        self.http.allow_redirects = environ.DATAGATOR_API_FOLLOW_REDIRECT
        self.http.timeout = environ.DATAGATOR_API_TIMEOUT

        # common http headers shared by all requests
        self.http.headers.update({
            "User-Agent": environ.DATAGATOR_API_USER_AGENT,
            "Accept-Encoding": environ.DATAGATOR_API_ACCEPT_ENCODING,
            "Content-Type": "application/json"})

        super(DataGatorService, self).__init__()
        pass

    @property
    def http(self):
        """
        underlying HTTP session (:class:`requests.Session`)
        """
        return self.__http

    def get(self, path):
        """
        :param path: relative url w.r.t. ``DATAGATOR_API_URL``.
        :returns: HTTP response object.
        """
        r = self.http.request(
            method="GET",
            url="{0}{1}".format(
                environ.DATAGATOR_API_URL,
                path if path.startswith("/") else "/{0}".format(path)))
        return r

    def put(self, path, data):
        """
        :param path: relative url w.r.t. ``DATAGATOR_API_URL``.
        :param data: JSON-serializable data object.
        :returns: HTTP response object.
        """
        r = self.http.request(
            method="PUT",
            url="{0}{1}".format(
                environ.DATAGATOR_API_URL,
                path if path.startswith("/") else "/{0}".format(path)),
            data=to_bytes(json.dumps(data)),
            auth=self.__auth)
        return r

    @property
    def status(self):
        """
        general status of the backend service
        """
        return self.get("/").json()

    @property
    def schema(self):
        """
        JSON schema being used by the backend service
        """
        return self.get("schema").json()

    def __del__(self):
        # close the underlying HTTP session upon garbage collection
        try:
            self.http.close()
        except Exception as e:
            _log.debug(e)
        pass

    pass
