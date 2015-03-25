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
import atexit
import importlib
import json
import jsonschema
import os
import shutil

from . import environ
from ._backend import DataGatorService
from ._cache import CacheManager
from ._compat import with_metaclass, to_bytes, to_native, to_unicode


__all__ = ['Entity', ]
__all__ = [to_native(n) for n in __all__]


class EntityType(type):

    def __new__(cls, name, parent, prop):

        # initialize singleton backend service shared by all entities
        repo, sep, key = environ.DATAGATOR_CREDENTIALS.partition(":")
        auth = (repo, key) if repo and key else None
        service = DataGatorService(auth=auth)
        prop['service'] = service
        prop['schema'] = jsonschema.Draft4Validator(service.schema)

        # initialize singleton cache manager shared by all entities
        try:
            mod, sep, cm_cls = environ.DATAGATOR_CACHE_BACKEND.rpartition(".")
            CacheManagerBackend = getattr(importlib.import_module(mod), cm_cls)
            assert(issubclass(CacheManagerBackend, CacheManager))
        except (ImportError, AssertionError):
            raise AssertionError("invalid cache backend '{0}'".format(
                environ.DATAGATOR_CACHE_BACKEND))
        else:
            prop['__cache__'] = CacheManagerBackend()

        return type(to_native(name), parent, prop)

    pass


class Entity(with_metaclass(EntityType, object)):
    """
    Abstract base class of all client-side entities
    """

    @classmethod
    def cleanup(cls):
        # decref triggers garbage collection of the cache manager backend
        setattr(cls, "__cache__", None)
        pass

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
                raise AssertionError("invalid response from backend service")
            # response should pass schema validation
            data = response.json()
            try:
                self.schema.validate(data)
            except jsonschema.ValidationError:
                raise AssertionError("invalid response from backend service")
            # error responses always come with code and message
            if response.status_code != 200:
                msg = "failed to load entity from backend service"
                if data.get("kind") == "datagator#Error":
                    msg = "{0} ({1}): {2}".format(
                        msg, data.get("code", "N/A"), data.get("message", ""))
                raise AssertionError(msg)
            # valid response should bare a matching entity kind
            assert(data.get("kind") == "datagator#{0}".format(self.kind)), \
                "unexpected entity kind '{0}'".format(data.get("kind"))
            # cache data for reuse
            if response.headers.get('Cache-Control', None) != "no-cache":
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

    @property
    @abc.abstractmethod
    def id(self):
        return None

    def __json__(self):
        return self.cache

    def __repr__(self):
        return "<{0} '{1}' at 0x{2:x}>".format(
            self.__class__.__name__, self.uri, id(self))

    pass


atexit.register(Entity.cleanup)
