# -*- coding: utf-8 -*-
"""
    datagator.wsgi.settings.dev
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.
"""

import os

from ..default import *

DEBUG = True

SECRET_KEY = "*nkx!@zbnt#)j$koa@e&1v4y%-wm&b+!4_3@=s5q@80^1g(-jm"

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
}
