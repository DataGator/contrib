# -*- coding: utf-8 -*-
"""
    test.config
    ~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/01/19
"""

from __future__ import unicode_literals, with_statement

__all__ = ['unittest', 'load_data', 'to_native', 'to_unicode',
           'get_credentials', 'DEBUG', ]


import atexit
import logging
import os
import os.path
import platform
import shutil
import sys
import tempfile

# local package takes precedence

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")))

# switch on / off debugging mode
DEBUG = os.environ.get("DEBUG", False) and not os.environ.get("NDEBUG", False)

logging.basicConfig()

if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(logging.WARNING)


# python 2 or 3 native string (from https://github.com/mitsuhiko/werkzeug/)

PY2 = (sys.version_info[0] == 2)

if PY2:

    def to_native(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None or isinstance(x, str):
            return x
        return x.encode(charset, errors)

else:

    def to_native(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None or isinstance(x, str):
            return x
        return x.decode(charset, errors)

__all__ = [to_native(n) for n in __all__]


def to_unicode(x, charset=sys.getdefaultencoding(), errors='strict',
               allow_none_charset=False):
    if x is None:
        return None
    if not isinstance(x, bytes):
        return text_type(x)
    if charset is None and allow_none_charset:
        return x
    return x.decode(charset, errors)


# package names unification

try:
    # python 2.6+
    import json
except ImportError:
    # python 2.5
    import simplejson as json

try:
    # python 2.6
    import unittest2 as unittest
except ImportError:
    # python 2.7+
    import unittest


def get_credentials(user_input=True, prompt="DataGator credentials: "):
    """
    Gets api credentials from environment variables, and optionally from user.
    """
    credentials = os.environ.get('DATAGATOR_CREDENTIALS', None) or \
        (user_input and raw_input(prompt))
    repo, sep, key = credentials.partition(":")
    return repo, key


# utilities for managing package data

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def load_data(name):
    """
    Load text resource from package data.
    """
    content = None
    with open(os.path.join(DATA_DIR, name), 'rb') as f:
        content = f.read()
        f.close()
    return content


# utilities for managing temporary files

TEMP_DIR = tempfile.mkdtemp()


def save_temp(name, data=b"", mode=0o666):
    """
    Writes data to a temporary file in the file system. Returns the full path
    to the temporary file on success, and None otherwise.
    """
    path = os.path.join(TEMP_DIR, name)
    try:
        with open(path, 'wb') as f:
            f.write(data)
            f.close()
        os.chmod(path, mode)
        if not os.access(path, os.F_OK | os.R_OK | os.W_OK):
            return None
        return path
    except:
        pass
    return None


def cleanup():
    """
    Erases temporary files and directories created during the test.
    """
    shutil.rmtree(TEMP_DIR)
    pass


atexit.register(cleanup)
