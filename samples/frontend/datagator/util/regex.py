# -*- coding: utf-8 -*-
"""
    datagator.util.regex
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.
"""

VAR_REGEX = r"[A-Za-z]\w{0,29}"

KEY_REGEX = r"""(?:[^"/?#@\\\s]|\\["'\\]){1,128}"""
