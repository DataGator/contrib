# -*- coding: utf-8 -*-
"""
    datagator.api.client._backend.environ
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/02/03
"""

from __future__ import unicode_literals, with_statement

import sys
import types

from .. import __version__ as __client_version__
from .._compat import to_native


class EnvironModule(types.ModuleType):

    __all__ = [to_native(n) for n in [
        'DATAGATOR_API_ACCEPT_ENCODING',
        'DATAGATOR_API_FOLLOW_REDIRECT',
        'DATAGATOR_API_TIMEOUT',
        'DATAGATOR_API_HOST',
        'DATAGATOR_API_SCHEME',
        'DATAGATOR_API_VERSION',
        'DATAGATOR_API_URL',
        'DATAGATOR_API_USER_AGENT', ]]

    __client_version__ = __client_version__

    __slots__ = ["DATAGATOR_API_ACCEPT_ENCODING",
                 "DATAGATOR_API_FOLLOW_REDIRECT",
                 "DATAGATOR_API_HOST",
                 "DATAGATOR_API_SCHEME",
                 "DATAGATOR_API_VERSION", ]

    def __init__(self, name, docs):
        import os
        self.DATAGATOR_API_HOST = os.environ.get(
            "DATAGATOR_API_HOST", "www.data-gator.com")
        self.DATAGATOR_API_SCHEME = os.environ.get(
            "DATAGATOR_API_SCHEME", "https")
        self.DATAGATOR_API_VERSION = os.environ.get(
            "DATAGATOR_API_VERSION", "v1")
        self.DATAGATOR_API_ACCEPT_ENCODING = "gzip, deflate, identity"
        self.DATAGATOR_API_FOLLOW_REDIRECT = False
        self.DATAGATOR_API_TIMEOUT = 180
        super(EnvironModule, self).__init__(name, docs)
        pass

    @property
    def DATAGATOR_API_URL(self):
        return "{0}://{1}/api/{2}".format(
            self.DATAGATOR_API_SCHEME,
            self.DATAGATOR_API_HOST,
            self.DATAGATOR_API_VERSION)

    @property
    def DATAGATOR_API_USER_AGENT(self):
        return "datagator-client (python/{0}.{1}.{2})".format(
            *self.__client_version__)

    pass

# override current module with an instance of EnvironManager to enable
# fine-granular access control on some *derived* environment variables.
sys.modules[__name__] = EnvironModule(__name__, __doc__)
