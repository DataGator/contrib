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

import io
import json
import logging
import os
import requests

from .. import environ
from .._compat import to_bytes, to_native

__all__ = ['DataGatorService', ]
__all__ = [to_native(n) for n in __all__]


_log = logging.getLogger(__package__)


def safe_url(path):

    request_uri = path

    # converting absolute url to relative path (ignore HTTP scheme)
    if "://" in request_uri:
        _, _, request_uri = request_uri.partition("://")
        _, _, expected_prefix = environ.DATAGATOR_API_URL.partition("://")
        if request_uri.startswith(expected_prefix):
            request_uri = request_uri[len(expected_prefix):]
        else:
            raise AssertionError("unexpected address: '{0}'".format(path))

    # unify relative path
    if request_uri.startswith("/"):
        request_uri = request_uri[1:]

    # finalize url
    return "{0}/{1}".format(environ.DATAGATOR_API_URL, request_uri)


def make_payload(data):
    if hasattr(data, "read"):
        return data
    return to_bytes(json.dumps(data))


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

        self.auth = auth

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
            "Accept": "application/json, */*",
            "Accept-Encoding": environ.DATAGATOR_API_ACCEPT_ENCODING})

        super(DataGatorService, self).__init__()
        pass

    @property
    def auth(self):
        return self.__auth

    @auth.setter
    def auth(self, auth):
        if auth:
            _log.info("enabled HTTP authentication")
            self.__auth = auth
        else:
            self.__auth = None
        pass

    @property
    def http(self):
        """
        underlying HTTP session (:class:`requests.Session`)
        """
        return self.__http

    def delete(self, path, headers={}):
        """
        :param path: relative url w.r.t. ``DATAGATOR_API_URL``.
        :param headers: extra HTTP headers to be sent with request.
        :returns: HTTP response object.
        """
        r = self.http.request(
            method="DELETE",
            url=safe_url(path),
            headers=headers)
        return r

    def get(self, path, headers={}, stream=False,
            timeout=environ.DATAGATOR_API_TIMEOUT):
        """
        :param path: relative url w.r.t. ``DATAGATOR_API_URL``.
        :param headers: extra HTTP headers to be sent with request.
        :param stream: enable streamed access to response body.
        :param timeout: connection timeout in seconds.
        :returns: HTTP response object.
        """
        r = self.http.request(
            method="GET",
            url=safe_url(path),
            headers=headers,
            stream=stream,
            timeout=timeout)
        return r

    def head(self, path, headers={}):
        """
        :param path: relative url w.r.t. ``DATAGATOR_API_URL``.
        :param headers: extra HTTP headers to be sent with request.
        :returns: HTTP response object.
        """
        r = self.http.request(
            method="HEAD",
            url=safe_url(path),
            headers=headers)
        return r

    def patch(self, path, data, headers={}):
        """
        :param path: relative url w.r.t. ``DATAGATOR_API_URL``.
        :param data: JSON-serializable data object.
        :param headers: extra HTTP headers to be sent with request.
        :returns: HTTP response object.
        """
        headers.setdefault('Content-Type', "application/json")
        r = self.http.request(
            method="PATCH",
            url=safe_url(path),
            data=make_payload(data),
            auth=self.__auth,
            headers=headers)
        return r

    def post(self, path, data, files={}, headers={}):
        """
        :param path: relative url w.r.t. ``DATAGATOR_API_URL``.
        :param data: JSON-serializable data object.
        :param file: dictionary of files ``{<key>: (<filename>, <file>)}``.
        :param headers: extra HTTP headers to be sent with request.
        :returns: HTTP response object.
        """

        if files:
            headers.setdefault('Content-Type', "multipart/form-data")
        else:
            data = make_payload(data)
            headers.setdefault('Content-Type', "application/json")

        r = self.http.request(
            method="POST",
            url=safe_url(path),
            data=data,
            files=files,
            auth=self.__auth,
            headers=headers)
        return r

    def put(self, path, data, headers={}):
        """
        :param path: relative url w.r.t. ``DATAGATOR_API_URL``.
        :param data: JSON-serializable data object.
        :param headers: extra HTTP headers to be sent with request.
        :returns: HTTP response object.
        """
        headers.setdefault('Content-Type', "application/json")
        r = self.http.request(
            method="PUT",
            url=safe_url(path),
            data=make_payload(data),
            auth=self.__auth,
            headers=headers)
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
        return self.get("/schema").json()

    def __del__(self):
        # close the underlying HTTP session upon garbage collection
        try:
            self.http.close()
        except Exception as e:
            _log.debug(e)
        pass

    pass
