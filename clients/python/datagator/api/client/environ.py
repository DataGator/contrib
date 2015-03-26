# -*- coding: utf-8 -*-
"""
    datagator.api.client.environ
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/02/03
"""

from __future__ import unicode_literals, with_statement

import sys
import types

from ._compat import to_native


class EnvironModule(types.ModuleType):

    __all__ = [to_native(n) for n in [
        'DATAGATOR_API_ACCEPT_ENCODING',
        'DATAGATOR_API_FOLLOW_REDIRECT',
        'DATAGATOR_API_TIMEOUT',
        'DATAGATOR_API_HOST',
        'DATAGATOR_API_SCHEME',
        'DATAGATOR_API_VERSION',
        'DATAGATOR_API_URL',
        'DATAGATOR_API_USER_AGENT',
        'DATAGATOR_CACHE_BACKEND',
        'DATAGATOR_CREDENTIALS',
        'DEBUG', ]]

    # version tuple of the pythonic HTTP client library
    __client_version__ = (0, 1, 1)

    __slots__ = ["DATAGATOR_API_ACCEPT_ENCODING",
                 "DATAGATOR_API_FOLLOW_REDIRECT",
                 "DATAGATOR_API_HOST",
                 "DATAGATOR_API_SCHEME",
                 "DATAGATOR_API_VERSION",
                 "DATAGATOR_CACHE_BACKEND",
                 "DEBUG", ]

    def __init__(self, name, docs):
        import os
        # domain name or IP address of backend service portal
        self.DATAGATOR_API_HOST = os.environ.get(
            "DATAGATOR_API_HOST", "www.data-gator.com")
        # HTTP or HTTPS
        self.DATAGATOR_API_SCHEME = os.environ.get(
            "DATAGATOR_API_SCHEME", "https")
        # API version (reserved for future extension)
        self.DATAGATOR_API_VERSION = os.environ.get(
            "DATAGATOR_API_VERSION", "v2")
        # disk-persistent cache manager backend
        self.DATAGATOR_CACHE_BACKEND = os.environ.get(
            "DATAGATOR_CACHE_BACKEND",
            "datagator.api.client._cache.leveldb.LevelDbCache")
        # debugging mode (``NDEBUG=1`` takes precedence over ``DEBUG=1``)
        self.DEBUG = int(os.environ.get("DEBUG", 0)) and \
            not int(os.environ.get("NDEBUG", 0))
        # encodings recognized by the HTTP library (favors gzip over identity)
        self.DATAGATOR_API_ACCEPT_ENCODING = "gzip, deflate, identity"
        # allow server-side redirection
        self.DATAGATOR_API_FOLLOW_REDIRECT = True
        # timeout of HTTP connection
        self.DATAGATOR_API_TIMEOUT = 180
        super(EnvironModule, self).__init__(name, docs)
        pass

    @property
    def DATAGATOR_API_URL(self):
        """
        URL prefix of all RESTful API endpoints
        """
        return "{0}://{1}/api/{2}".format(
            self.DATAGATOR_API_SCHEME,
            self.DATAGATOR_API_HOST,
            self.DATAGATOR_API_VERSION)

    @property
    def DATAGATOR_API_USER_AGENT(self):
        """
        User-Agent request header (see :RFC:`2616`)
        """
        return "datagator-api-client (python/{0}.{1}.{2})".format(
            *self.__client_version__)

    pass


# override current Python module with an instance of EnvironModule to enable
# fine-granular access control on some *derived* environment variables.
sys.modules[__name__] = EnvironModule(__name__, __doc__)
