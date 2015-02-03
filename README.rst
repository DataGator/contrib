Resource for ``DataGator`` Contributors
---------------------------------------

The ``DataGator`` project aims to realize the crowd-source data analytics platform as envisioned by the `Frederick S. Pardee Center for International Futures <http://pardee.du.edu>`_ (abbr. `Pardee`) at the University of Denver.
Once evolved to its full-fledged form, ``DataGator`` will serve as a collaboration tool for sharing, cleansing, and augmenting data sets among an online research community, which gears up domain-specific studies with data science methodologies including exploration, visualization, and quantitative analytics.
This repository collects public resources including specification documents, sample data, and code snippets for prospective contributors of the ``DataGator`` project.


``tests``
~~~~~~~~~

.. image:: https://travis-ci.org/liuyu81/datagator-contrib.svg?branch=master
   :target: https://travis-ci.org/liuyu81/datagator-contrib
   :alt: Build Status

The public test suite of ``DataGator`` (aka. ``tests``) is designed for (i) validation of ``DataGator``'s backend services through the RESTful API, and (ii) coverage testing of ``DataGator``'s HTTP client libraries.

Basic usage is simply,

.. code-block:: bash

    $ python -m tests -v

Optional settings can be passed via the following environment variables,

+---------------------------+--------------------------------------------------+
| **Variable**              | **Description**                                  |
+---------------------------+--------------------------------------------------+
| ``DATAGATOR_API_HOST``    | name or IP address of ``DataGator``'s backend    |
|                           | portal, defaults to ``www.data-gator.com``       |
+---------------------------+--------------------------------------------------+
| ``DATAGATOR_CREDENTIALS`` | access key in the form of ``<repo>:<secret>``    |
+---------------------------+--------------------------------------------------+
| ``DEBUG``                 | ``DEBUG=1`` turns on debugging mode              |
+---------------------------+--------------------------------------------------+
