# -*- coding: utf-8 -*-
"""
    datagator.api.client._entity
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/03/24
"""

from __future__ import unicode_literals, with_statement

import abc
import os
import json
import jsonschema

from ._backend import DataGatorService
from ._compat import with_metaclass, to_native, to_unicode


__all__ = ['Entity', ]
__all__ = [to_native(n) for n in __all__]


class CacheManager(dict):

    def delete(self, key):
        return self.pop(key, None)

    def put(self, key, value):
        self[key] = value
        pass

    def flush(self):
        return self.clear()

    pass


class EntityType(type):

    def __new__(cls, name, parent, prop):
        credentials = os.environ.get('DATAGATOR_CREDENTIALS', "")
        repo, sep, key = credentials.partition(":")
        auth = (repo, key) if repo and key else None
        prop['service'] = service = DataGatorService(auth=auth)
        prop['schema'] = jsonschema.Draft4Validator(service.schema)
        prop['__cache__'] = CacheManager()
        return type(to_native(name), parent, prop)

    pass


class Entity(with_metaclass(EntityType, object)):
    """
    Abstract base class of all client-side entities
    """

    @staticmethod
    def flush():
        """
        flush global entity cache
        """
        self.__cache__.flush()

    __slots__ = ['__kind', ]

    def __init__(self, kind):
        super(Entity, self).__init__()
        kind = to_unicode(kind)
        if kind.startswith("datagator#"):
            kind = kind[len("datagator#"):]
        self.__kind = kind
        pass

    @property
    def cache(self):
        data = self.__cache__.get(self.uri, None)
        if data is None:
            response = self.service.get(self.uri)
            # response body should be a valid JSON object even in case of error
            if response.headers['Content-Type'] != "application/json":
                raise ValueError("invalid response from backend service")
            # response should pass schema validation
            data = response.json()
            self.schema.validate(data)
            # error responses always come with code and message
            if response.status_code != 200:
                msg = "failed to load entity from backend service"
                if data.get("kind") == "datagator#Error":
                    msg = "{0} ({1}): {2}".format(
                        msg, data.get("code", "N/A"), data.get("message", ""))
                raise KeyError(msg)
            # valid response should bare a matching entity kind
            assert(data.get("kind") == "datagator#{0}".format(self.kind)), \
                "unexpected entity kind '{0}'".format(data.get("kind"))
            # cache data for reuse
            self.__cache__.put(self.uri, data)
        return data

    @cache.setter
    def cache(self, data):
        if data is not None:
            self.__cache__.put(self.uri, data)
        else:
            self.__cache__.delete(self.uri)
        pass

    @property
    def kind(self):
        return self.__kind

    @property
    @abc.abstractmethod
    def uri(self):
        return None

    def __json__(self):
        return self.cache

    def __repr__(self):
        return "<{0} '{1}' at 0x{2:x}>".format(
            self.__class__.__name__, self.uri, id(self))

    pass
