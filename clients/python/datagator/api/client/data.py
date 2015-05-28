# -*- coding: utf-8 -*-
"""
    datagator.api.client.data
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/03/24
"""

from __future__ import unicode_literals, with_statement

from ._compat import OrderedDict, with_metaclass, to_native, to_unicode
from ._entity import Entity, normalized


__all__ = ['Matrix', 'Recipe', ]
__all__ = [to_native(n) for n in __all__]


class DataItem(Entity):

    @staticmethod
    def get(ref):
        try:
            ds = DataSet.get(ref)
            assert("items" in ref or len(ref['items']) == 1)
            name = ref['items'][0]['name']
        except (jsonschema.ValidationError, AssertionError):
            raise ValueError("invalid data item reference")
        else:
            return ds[name]

    __slots__ = ['__dataset', '__key', ]

    def __new__(cls, kind, dataset, key):
        kind = normalized(kind)
        cls = globals().get(kind, DataItem)
        assert(issubclass(cls, DataItem)), \
            "unexpected data item kind '{0}'".format(kind)
        return object.__new__(cls)

    def __init__(self, kind, dataset, key):
        kind = normalized(kind)
        super(DataItem, self).__init__(kind)
        self.__dataset = dataset
        self.__key = key
        pass

    @property
    def uri(self):
        return "{0}/{1}".format(self.dataset.uri, self.key)

    @property
    def ref(self):
        # NOTE: the JSON-based reference of a `DataItem` reuses the schema of
        # `DataSet`, but `items` and `itemsCount` fields are always present.
        obj = self.dataset.ref
        obj['items'] = tuple([Entity.Ref([
            ("kind", "datagator#{0}".format(self.kind)),
            ("name", self.key),
        ]), ])
        obj['itemsCount'] = 1
        return obj

    @property
    def key(self):
        return self.__key

    @property
    def dataset(self):
        return self.__dataset

    pass


class Matrix(DataItem):

    pass


class Recipe(DataItem):

    pass


class Opaque(DataItem):

    pass
