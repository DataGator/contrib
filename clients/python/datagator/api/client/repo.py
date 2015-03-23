# -*- coding: utf-8 -*-
"""
    datagator.api.client.repo
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/01/28
"""

from __future__ import unicode_literals, with_statement

import abc
import json
import jsonschema
import os

from ._backend import DataGatorService
from ._compat import with_metaclass, to_native, to_unicode

__all__ = ['DataSet', 'Repo', ]
__all__ = [to_native(n) for n in __all__]


class EntityType(type):

    def __new__(cls, name, parent, prop):
        credentials = os.environ.get('DATAGATOR_CREDENTIALS', "")
        repo, sep, key = credentials.partition(":")
        auth = (repo, key) if repo and key else None
        service = DataGatorService(auth=auth)
        prop['service'] = service
        prop['schema'] = jsonschema.Draft4Validator(service.schema)
        prop['__cache__'] = {}
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
        self.__cache__.clear()

    __slots__ = ['__kind', ]

    def __init__(self, kind):
        super(Entity, self).__init__()
        self.__kind = to_unicode(kind)
        if self.__kind.startswith("datagator#"):
            self.__kind = self.__kind[len("datagator#"):]
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
            self.__cache__[self.uri] = data
        return data

    @cache.setter
    def cache(self, data):
        if data is not None:
            self.__cache__[self.uri] = data
        else:
            del self.__cache__[self.uri]
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


class DataSet(Entity):

    __slots__ = ['__name', '__repo', ]

    def __init__(self, name, repo):
        super(DataSet, self).__init__(self.__class__.__name__)
        self.__name = to_unicode(name)
        self.__repo = repo
        pass

    @property
    def uri(self):
        return "{0}/{1}".format(self.repo.name, self.name)

    @property
    def name(self):
        return self.__name

    @property
    def repo(self):
        return self.__repo

    def __iter__(self):
        for item in self.cache.get("items", []):
            yield item.get("name")
        pass

    def __len__(self):
        return self.cache.get("itemsCount", 0)

    pass


class Repo(Entity):

    __slots__ = ['__name', ]

    def __init__(self, name, credentials=None):
        super(Repo, self).__init__(self.__class__.__name__)
        self.__name = to_unicode(name)
        if credentials is not None:
            self.service.auth = (self.name, credentials)
        pass

    @property
    def uri(self):
        return self.name

    @property
    def name(self):
        return self.__name

    def __getitem__(self, name):
        return DataSet(name, self)

    def __setitem__(self, name, dataset):
        self.cache = None
        raise NotImplementedError()

    def __iter__(self):
        if "items" not in self.cache:
            # invalidate dirty cache
            self.cache = None
        for ds in self.cache.get("items", []):
            yield DataSet(ds.get("name"), self)
        pass

    def __len__(self):
        if "itemsCount" not in self.cache:
            # invalidate dirty cache
            self.cache = None
        return self.cache.get("itemsCount", 0)

    pass
