# -*- coding: utf-8 -*-
"""
    datagator.wsgi.settings
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.
"""

import os

if not int(os.environ.get("DATAGATOR_DEVELOP", 0)):
    from .rel import *
else:
    from .dev import *
