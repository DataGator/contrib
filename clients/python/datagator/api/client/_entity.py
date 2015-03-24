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
import io
import json
import jsonschema
import leveldb
import os
import shutil
import tempfile

from ._backend import DataGatorService
from ._compat import with_metaclass, to_bytes, to_native, to_unicode


__all__ = ['Entity', ]
__all__ = [to_native(n) for n in __all__]


class CacheManager(object):
    """
    Disk-backed cache manager
    """

    __slots__ = ['__db', '__fs', ]

    def __init__(self, fs=None):
        self.__fs = fs or tempfile.mkdtemp(suffix=".DataGatorCache")
        self.__db = None
        pass

    @property
    def db(self):
        if self.__db is None:
            self.__db = leveldb.LevelDB(filename=to_native(self.__fs))
        return self.__db

    def get(self, key, value=None):
        fetched = None
        try:
            fetched = to_unicode(self.db.Get(to_bytes(key)))
        except KeyError:
            pass
        return json.loads(fetched) if fetched else value

    def put(self, key, value):
        return self.db.Put(to_bytes(key), to_bytes(json.dumps(value)))

    def delete(self, key):
        return self.db.Delete(to_bytes(key))

    def __del__(self):
        try:
            self.__db = None
            leveldb.DestroyDB(to_native(self.__fs))
            shutil.rmtree(self.__fs)
            self.__fs = None
        except:
            pass
        finally:
            self.__db = self.__fs = None
        pass

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

    @classmethod
    def cleanup(cls):
        setattr(cls, "__cache__", None)

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


atexit.register(Entity.cleanup)
