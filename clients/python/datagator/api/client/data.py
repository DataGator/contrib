# -*- coding: utf-8 -*-
"""
    datagator.api.client.repo
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/03/24
"""

from __future__ import unicode_literals, with_statement

from ._compat import with_metaclass, to_native, to_unicode
from ._entity import Entity


__all__ = ['Matrix', 'Recipe', ]
__all__ = [to_native(n) for n in __all__]


class DataItem(Entity):

    pass


class Matrix(DataItem):

    pass


class Recipe(DataItem):

    pass
