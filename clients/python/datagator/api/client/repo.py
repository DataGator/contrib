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

import jsonschema

from . import environ
from ._compat import to_native, to_unicode
from ._entity import Entity


__all__ = ['DataSet', 'Repo', ]
__all__ = [to_native(n) for n in __all__]


class DataSet(Entity):

    __slots__ = ['__name', '__repo', ]

    def __init__(self, name, repo):
        super(DataSet, self).__init__(self.__class__.__name__)
        self.__name = to_unicode(name)
        self.__repo = repo
        try:
            # assertion of name and repo through schema validation
            expected = {
                "kind": "datagator#DataSet",
                "name": self.name,
                "repo": {"kind": "datagator#Repo", "name": self.repo.name}
            }
            self.schema.validate(expected)
        except jsonschema.ValidationError:
            raise AssertionError("invalid name or repository")
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

    @property
    def rev(self):
        if "rev" not in self.cache:
            self.cache = None
        return self.cache.get("rev", 0)

    def __iter__(self):
        if "items" not in self.cache:
            # invalidate dirty cache
            self.cache = None
        for item in self.cache.get("items", []):
            yield item.get("name")
        pass

    def __len__(self):
        if "itemsCount" not in self.cache:
            # invalidate dirty cache
            self.cache = None
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

    def __contains__(self, dsname):
        try:
            # if `dsname` is not a valid name for a DataSet entity, then it
            # cannot exist in the storage backend.
            ds = DataSet(dsname, self)
            # looking up `Entity.__cache__` is more preferrable than `ds.cache`
            # because the latter may trigger connection to the backend service
            if Entity.__cache__.exists(ds.uri):
                return True
            return ds.cache is not None
        except (AssertionError, KeyError):
            return False
        return False  # should NOT reach here

    def __getitem__(self, dsname):
        if dsname in self:
            return DataSet(dsname, self)
        raise KeyError("invalid dataset")

    def __setitem__(self, dsname, dataset):
        self.cache = None
        try:
            ds = DataSet(dsname, self).cache = None
        except AssertionError:
            raise KeyError("invalid dataset")
        raise NotImplementedError()

    def __delitem__(self):
        self.cache = None
        try:
            ds = DataSet(name, self).cache = None
        except AssertionError:
            raise KeyError("invalid dataset")
        raise NotImplementedError()

    def __iter__(self):
        if "items" not in self.cache:
            # invalidate dirty cache
            self.cache = None
        for ds in self.cache.get("items", []):
            yield ds.get("name")
        pass

    def __len__(self):
        if "itemsCount" not in self.cache:
            # invalidate dirty cache
            self.cache = None
        return self.cache.get("itemsCount", 0)

    pass
