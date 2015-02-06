# -*- coding: utf-8 -*-
"""
    datagator.api.client
    ~~~~~~~~~~~~~~~~~~~~

    HTTP Client Library for `DataGator`_.

    .. _`DataGator`: http://www.data-gator.com/

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/01/28
"""

from __future__ import unicode_literals, with_statement
from ._compat import to_native

__all__ = ['Repo', ]
__all__ = [to_native(n) for n in __all__]


# package metadata

__version__ = (0, 0, 3)
__author__ = "LIU Yu"
__contact__ = "liuyu@opencps.net"


from .repo import Repo
