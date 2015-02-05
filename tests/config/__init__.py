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
           'get_credentials', ]


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

from datagator.api.client._compat import to_unicode, to_native

__all__ = [to_native(n) for n in __all__]


# switch on / off debugging mode

from datagator.api.client._backend import environ

logging.basicConfig()
logging.getLogger().setLevel(
    logging.DEBUG if environ.DEBUG else logging.WARNING)


# PY 2 / 3 unification

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
    Get access key to DataGator's backend service from an environment variable
    named ``DATAGATOR_CREDENTIALS``, and fallback to user input.
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
