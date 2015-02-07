# -*- coding: utf-8 -*-
"""
    datagator.api.client._backend
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Low-Level Abstraction of `DataGator`_'s Backend Service

    .. _`DataGator`: http://www.data-gator.com/

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/01/28
"""

from __future__ import unicode_literals

from .service import DataGatorService
from .._compat import to_native

__all__ = ['DataGatorService', ]
__all__ = [to_native(n) for n in __all__]
