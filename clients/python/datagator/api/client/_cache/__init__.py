# -*- coding: utf-8 -*-
"""
    datagator.api.client._cache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/03/25
"""

from __future__ import unicode_literals, with_statement

import abc

from .._compat import to_native


__all__ = ['CacheManager', ]
__all__ = [to_native(n) for n in __all__]


class CacheManager(object):
    """
    Abstract base class of disk-persisted cache manager
    """

    @abc.abstractmethod
    def get(self, key, value=None):
        pass

    @abc.abstractmethod
    def put(self, key, value):
        pass

    @abc.abstractmethod
    def delete(self, key):
        pass

    @abc.abstractmethod
    def exists(self, key):
        pass

    pass
