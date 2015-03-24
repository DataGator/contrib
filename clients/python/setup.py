#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    HTTP Client Library for `DataGator`_
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. _`DataGator`: http://www.data-gator.com/

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/02/10
"""

import os
import sys

from distutils.core import setup
from glob import glob
from os.path import isfile, join

PACKAGE = "datagator-api-client"


# auxiliary data files for installation
def get_data_files():
    #
    data_files = []
    if sys.platform == "win32":
        datadir = join("doc", PACKAGE)
    else:
        datadir = join("share", "doc", PACKAGE)
    #
    files = ["README.rst", "LICENSE", ]
    if files:
        data_files.append((join(datadir), files))
    #
    files = glob(join("docs", "*.rst"))
    if files:
        data_files.append((join(datadir, "docs"), files))
    #
    files = glob(join("tests", "*.py"))
    if files:
        data_files.append((join(datadir, "tests"), files))
    #
    files = glob(join("tests", "config", "*.*"))
    if files:
        data_files.append((join(datadir, "tests", "config"), files))
    #
    assert data_files
    for install_dir, files in data_files:
        assert files
        for f in files:
            assert isfile(f), (f, install_dir)
    return data_files


# make sure local package takes precedence over installed (old) package
sys.path.insert(0, join("src", ))
pkg = __import__('datagator.api.client', fromlist=["datagator.api"])


setup(
    name=PACKAGE,
    packages=["datagator.api.client", "datagator.api.client._backend"],
    package_dir={
        "datagator": join(".", "datagator", ),
        "datagator.api": join(".", "datagator", "api"),
        "datagator.api.client": join(".", "datagator", "api", "client"), },
    package_data={},
    data_files=get_data_files(),
    version=".".join(map(str, pkg.__version__)),
    author=pkg.__author__,
    license=pkg.__license__,
    author_email=pkg.__contact__,
    description="HTTP Client Library for SnapSearch",
    long_description=open("README.rst").read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Operating System :: OS Independent",
        "Topic :: Database :: Front-Ends",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["DataGator", "client", "data science", "HTTP", "Pardee"],
    platforms="All",
    provides=["datagator.api.client", ],
    requires=["requests", "jsonschema", "leveldb", ],
    url="https://github.com/DataGator/",
)
