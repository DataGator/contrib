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
import io
import json
import jsonschema
import logging
import os
import tempfile

from . import environ
from ._backend import DataGatorService
from ._cache import CacheManager
from ._compat import with_metaclass, to_bytes, to_native, to_unicode


__all__ = ['Entity', 'validated', ]
__all__ = [to_native(n) for n in __all__]


_log = logging.getLogger(__name__)


class validated(object):
    """
    Context manager and proxy to validated response from backend service
    """

    __slots__ = ['__response', '__expected_status', '__body', '__size', ]

    def __init__(self, response, verify_code=True):
        """
        :param response: response object from the backend service
        :param exptected: `list` or `tuple` of expected status codes
        """
        self.__response = response
        self.__expected_status = tuple(verify_code) \
            if isinstance(verify_code, (list, tuple)) else (200, ) \
            if verify_code else None
        self.__body = None
        self.__size = 0
        pass

    @property
    def status_code(self):
        return self.__response.status_code

    @property
    def headers(self):
        return self.__response.headers

    @property
    def body(self):
        return self.__body

    def __len__(self):
        return self.__size

    def __enter__(self):
        # validate content-type and body data
        _log.debug("validating response")
        _log.debug("  - from: {0}".format(self.__response.url))
        _log.debug("  - status code: {0}".format(self.__response.status_code))
        _log.debug("  - response time: {0}".format(self.__response.elapsed))
        try:
            # response body should be a valid JSON object
            assert(self.headers['Content-Type'] == "application/json")
            data = None
            chunk_size = 2 ** 16
            with tempfile.SpooledTemporaryFile(
                    max_size=chunk_size, mode="w+b",
                    suffix=".DataGatorEntity") as f:
                # make sure f conforms to the prototype of IOBase
                for attr in ("readable", "writable", "seekable"):
                    if not hasattr(f, attr):
                        setattr(f, attr, lambda: True)
                # wrie decoded response body
                for chunk in self.__response.iter_content(
                        chunk_size=chunk_size, decode_unicode=True):
                    if not chunk:
                        continue
                    f.write(chunk)
                self.__size = f.tell()
                _log.debug("  - decoded size: {0}".format(len(self)))
                # py3k cannot `json.load()` binary files directly, it needs a
                # text IO wrapper to handle decoding (to unicode / str)
                f.seek(0)
                data = json.load(io.TextIOWrapper(f))
                f.close()
            Entity.__schema__.validate(data)
            self.__body = data
        except (jsonschema.ValidationError, AssertionError, IOError, ):
            # re-raise as runtime error
            raise RuntimeError("invalid response from backend service")
        else:
            # validate status code
            if self.__expected_status is not None and \
                    self.status_code not in self.__expected_status:
                # error responses always come with code and message
                msg = "unexpected response from backend service"
                if data.get("kind") == "datagator#Error":
                    msg = "{0} ({1}): {2}".format(
                        msg, data.get("code", "N/A"), data.get("message", ""))
                # re-raise as runtime error
                raise RuntimeError(msg)
            pass
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        if isinstance(exc_value, Exception):
            _log.error("failed response validation")
        else:
            pass
        return False  # re-raise exception

    pass


class EntityType(type):
    """
    Meta class for initializing class members of the Entity class
    """

    def __new__(cls, name, parent, prop):

        # initialize cache manager shared by all entities
        try:
            mod, sep, cm_cls = environ.DATAGATOR_CACHE_BACKEND.rpartition(".")
            CacheManagerBackend = getattr(importlib.import_module(mod), cm_cls)
            assert(issubclass(CacheManagerBackend, CacheManager))
        except (ImportError, AssertionError):
            raise AssertionError("invalid cache backend '{0}'".format(
                environ.DATAGATOR_CACHE_BACKEND))
        else:
            prop['__cache__'] = CacheManagerBackend()

        # initialize backend service shared by all entities
        try:
            service = DataGatorService()
        except:
            raise RuntimeError("failed to initialize backend service")
        else:
            prop['__service__'] = service

        # initialize schema validator shared by all entities
        try:
            # load schema from local file if exists (fast but may be staled)
            filename = os.path.join(os.path.dirname(__file__), "schema.json")
            schema = None
            if os.access(filename, os.F_OK | os.R_OK):
                with open(filename, "r") as f:
                    schema = json.load(f)
                    f.close()
            # load schema from service backend (slow but always up-to-date)
            if schema is None:
                schema = prop['__service__'].schema
        except:
            raise RuntimeError("failed to initialize schema validator")
        else:
            prop['__schema__'] = jsonschema.Draft4Validator(schema)

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
    def kind(self):
        return self.__kind

    @property
    @abc.abstractmethod
    def uri(self):
        return None

    @property
    @abc.abstractmethod
    def ref(self):
        return None

    # `cache` is defined with standalone getter / setter methods, because a
    # subclass may need to extend these methods though `super(SubClass, self)`

    def _cache_getter(self):
        data = Entity.__cache__.get(self.uri, None)
        if data is None:
            with validated(Entity.__service__.get(self.uri, stream=True)) as r:
                data = r.body
                kind = data.get("kind")
                # valid response should bare a matching entity kind
                assert(kind == "datagator#{0}".format(self.kind)), \
                    "unexpected entity kind '{0}'".format(kind)
                # cache data for reuse (iff. advised by the backend)
                if r.headers.get("Cache-Control", "private") != "no-cache":
                    Entity.__cache__.put(self.uri, data)
        return data

    def _cache_setter(self, data):
        if data is not None:
            Entity.__cache__.put(self.uri, data)
        else:
            Entity.__cache__.delete(self.uri)
        pass

    cache = property(_cache_getter, _cache_setter)

    def __json__(self):
        return self.cache

    def __repr__(self):
        return "<{0} '{1}' at 0x{2:x}>".format(
            self.__class__.__name__, self.uri, id(self))

    pass


atexit.register(Entity.cleanup)
