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
from ._compat import to_native

__all__ = ['Repo', ]
__all__ = [to_native(n) for n in __all__]


from ._backend import DataGatorService


class Repo(DataGatorService):

    __slots__ = ['__name', ]

    def __init__(self, name, credential=None):
        self.__name = name
        auth = None if not credential else (self.name, credential)
        super(Repo, self).__init__(auth=auth)
        pass

    def __iter__(self):
        pass

    @property
    def name(self):
        return self.__name

    def auth(self, credential):
        self.http.auth = (self.name, credential)
        pass

    pass
