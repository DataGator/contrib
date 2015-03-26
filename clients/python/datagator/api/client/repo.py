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
from ._entity import Entity, validated


__all__ = ['DataSet', 'Repo', ]
__all__ = [to_native(n) for n in __all__]


class DataSet(Entity):

    __slots__ = ['__name', '__repo', ]

    def __init__(self, name, repo):
        super(DataSet, self).__init__(self.__class__.__name__)
        self.__name = to_unicode(name)
        self.__repo = repo
        try:
            # the data set may not have been committed to the backend service
            # so we just verify the identifier is valid by the schema
            Entity.__schema__.validate(self.ref)
        except jsonschema.ValidationError:
            raise AssertionError("invalid dataset name")
        pass

    @property
    def uri(self):
        return "{0}/{1}".format(self.repo.name, self.name)

    @property
    def ref(self):
        return dict([
            ("kind", "datagator#DataSet"),
            ("name", self.name),
            ("repo", self.repo.ref),
        ])

    @property
    def name(self):
        return self.__name

    @property
    def repo(self):
        return self.__repo

    @property
    def rev(self):
        content = self.cache
        if "rev" not in content:
            self.cache = None
            content = self.cache
        return content.get("rev", 0)

    def __iter__(self):
        for item in self.cache.get("items", []):
            yield item.get("name")
        pass

    def __len__(self):
        return self.cache.get("itemsCount", 0)

    pass


class Repo(Entity):

    __slots__ = ['__name', ]

    def __init__(self, name, access_key=None):
        super(Repo, self).__init__(self.__class__.__name__)
        self.__name = to_unicode(name)
        if self.cache is None:
            raise AssertionError("invalid repository '{0}'".format(self.name))
        if access_key is not None:
            Entity.__service__.auth = (self.name, access_key)
        pass

    @property
    def uri(self):
        return self.name

    @property
    def name(self):
        return self.__name

    @property
    def ref(self):
        return dict([
            ("kind", "datagator#Repo"),
            ("name", self.name),
        ])

    def __contains__(self, dsname):
        try:
            # if `dsname` is not a valid name for a DataSet entity, then it is
            # guaranteed to *not* exist in the storage backend.
            ref = DataSet(dsname, self)
            # looking up `Entity.__cache__` is more preferrable than `ds.cache`
            # because the latter may trigger connection to the backend service
            if Entity.__cache__.exists(ref.uri):
                return True
            return ref.cache is not None
        except (AssertionError, RuntimeError, ):
            return False
        return False  # should NOT reach here

    def __getitem__(self, dsname):
        try:
            if dsname in self:
                return DataSet(dsname, self)
        except (AssertionError, ):
            pass
        raise KeyError("invalid dataset")

    def __setitem__(self, dsname, items):
        ref = None
        try:
            ref = DataSet(dsname, self)
        except (AssertionError, ):
            raise KeyError("invalid dataset name")
        if isinstance(items, (dict, list, tuple)):
            # inspect and serialize content
            pass
        elif not isinstance(items, DataSet):
            raise ValueError("invalid dataset value")
        elif items.uri != ref.uri:
            raise ValueError("inconsistent dataset name and value")
        # create / update dataset
        with validated(Entity.__service__.put(ref.uri, ref.ref), (200, 201)):
            # invalidate local cache
            ref.cache = None
            self.cache = None
        # TODO: commit content
        pass

    def __delitem__(self, dsname):
        raise NotImplementedError()

    def __iter__(self):
        for ref in self.cache.get("items", []):
            yield ref.get("name")
        pass

    def __len__(self):
        return self.cache.get("itemsCount", 0)

    pass
