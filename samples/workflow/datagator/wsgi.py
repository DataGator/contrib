# -*- coding: utf-8 -*-
"""
    datagator.views
    ~~~~~~~~~~~~~~~

    WSGI config for the `DataGator`_ project.

    .. _`DataGator`: https://www.data-gator.com/

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "datagator.settings")

application = get_wsgi_application()
