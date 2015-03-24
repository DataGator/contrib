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
