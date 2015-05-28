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
from ._compat import OrderedDict, with_metaclass
from ._compat import to_bytes, to_native, to_unicode


__all__ = ['Entity', 'validated', 'normalized', ]
__all__ = [to_native(n) for n in __all__]


_log = logging.getLogger(__name__)


def normalized(kind):
    """
    Normalized entity kind without leading "datagator#"
    """
    kind = to_unicode(kind or "")
    if kind.startswith("datagator#"):
        kind = kind[len("datagator#"):]
    return kind or None


class validated(object):
    """
    Context manager and proxy to validated response from backend service
    """

    DEFAULT_CHUNK_SIZE = 2 ** 21  # 2MB

    __slots__ = ['__response', '__expected_status', '__raw_body',
                 '__decoded_body', '__size', ]

    def __init__(self, response, verify_status=True):
        """
        :param response: response object from the backend service
        :param exptected: `list` or `tuple` of expected status codes
        """
        assert(environ.DATAGATOR_API_VERSION == "v2"), \
            "incompatible backend service version"
        self.__response = response
        self.__expected_status = tuple(verify_status) \
            if isinstance(verify_status, (list, tuple)) else (200, ) \
            if verify_status else None
        self.__raw_body = None
        self.__decoded_body = None
        self.__size = 0
        pass

    @property
    def status_code(self):
        """
        HTTP status code of the underlying response
        """
        return self.__response.status_code

    @property
    def headers(self):
        """
        HTTP message headers of the underlying response
        """
        return self.__response.headers

    @property
    def body(self):
        """
        HTTP message body stored as a file-like object
        """
        if self.__raw_body is not None:
            self.__raw_body.seek(0)
        return self.__raw_body

    def json(self, validate_schema=True):
        """
        JSON-decoded message body of the underlying response
        """
        if self.__decoded_body is None:
            try:
                # py3k cannot `json.load()` binary files directly, it needs a
                # text IO wrapper to handle decoding (to unicode / str)
                data = json.load(io.TextIOWrapper(self.body))
                if validate_schema:
                    Entity.schema.validate(data)
            except (jsonschema.ValidationError, AssertionError, IOError, ):
                raise RuntimeError("invalid response from backend service")
            else:
                self.__decoded_body = data
        return self.__decoded_body

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
            f = tempfile.SpooledTemporaryFile(
                max_size=self.DEFAULT_CHUNK_SIZE, mode="w+b",
                suffix=".DataGatorEntity")
            # make sure f conforms to the prototype of `io.IOBase`
            for attr in ("readable", "writable", "seekable"):
                if not hasattr(f, attr):
                    setattr(f, attr, lambda: True)
            # wrie decoded response body
            for chunk in self.__response.iter_content(
                    chunk_size=self.DEFAULT_CHUNK_SIZE,
                    decode_unicode=True):
                if not chunk:
                    continue
                f.write(chunk)
            self.__raw_body = f
            self.__size = f.tell()
            _log.debug("  - decoded size: {0}".format(len(self)))
        except (AssertionError, IOError, ):
            # re-raise as runtime error
            raise RuntimeError("invalid response from backend service")
        else:
            # validate status code
            if self.__expected_status is not None and \
                    self.status_code not in self.__expected_status:
                # error responses always come with code and message
                data = self.json()
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
        # discard temporary file
        if self.__raw_body is not None:
            self.__raw_body.close()
            self.__raw_body = None
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
            prop['store'] = CacheManagerBackend()

        # initialize backend service shared by all entities
        try:
            service = DataGatorService()
        except:
            raise RuntimeError("failed to initialize backend service")
        else:
            prop['service'] = service

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
                schema = prop['service'].schema
        except:
            raise RuntimeError("failed to initialize schema validator")
        else:
            prop['schema'] = jsonschema.Draft4Validator(schema)

        return type(to_native(name), parent, prop)

    pass


class Entity(with_metaclass(EntityType, object)):
    """
    Abstract base class of all client-side entities
    """

    class Ref(OrderedDict):

        def __hash__(self):
            return json.dumps(self).__hash__()

        pass

    @classmethod
    def cleanup(cls):
        # decref triggers garbage collection of the cache manager backend
        setattr(cls, "store", None)
        pass

    __slots__ = ['__kind', ]

    def __init__(self, kind):
        super(Entity, self).__init__()
        self.__kind = normalized(kind)
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

    # `cache` is defined with old-school getter / deleter methods, because a
    # subclass may need to access `super(SubClass, self)._cache_getter()` and
    # `._cache_deleter()` to extend / override the default caching behaviour.

    def _cache_getter(self):
        data = Entity.store.get(self.uri, None)
        if data is None:
            with validated(Entity.service.get(self.uri, stream=True)) as r:
                # valid response should bear a matching entity kind
                kind = normalized(r.headers.get("X-DataGator-Entity", None))
                assert(kind == self.kind), \
                    "unexpected entity kind '{0}'".format(kind)
                # cache data for reuse (iff. advised by the backend)
                if r.headers.get("Cache-Control", "private") != "no-cache":
                    # cache backend typically only support byte-string values,
                    # so passing `r.body` (file-like object) instead of `data`
                    # (dictionary) can save an extra round of JSON-encoding.
                    Entity.store.put(self.uri, r.body)
                # this should come last since calling `r.json()` will close the
                # temporary file under `r.body` implicitly (observed in py27).
                data = r.json()
        return data

    def _cache_deleter(self):
        Entity.store.delete(self.uri)
        pass

    cache = property(_cache_getter, None, _cache_deleter)

    def __json__(self):
        return self.cache

    def __repr__(self):
        return "<{0} '{1}' at 0x{2:x}>".format(
            self.__class__.__name__, self.uri, id(self))

    pass


atexit.register(Entity.cleanup)
