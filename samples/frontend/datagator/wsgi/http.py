# -*- coding: utf-8 -*-
"""
    datagator.wsgi.http
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.
"""

from django.http import HttpResponse


__all__ = ['HttpResponseUnauthorized', ]


class HttpResponseUnauthorized(HttpResponse):

    status_code = 401

    def __init__(self, *args, **kwargs):
        super(HttpResponseUnauthorized, self).__init__(*args, **kwargs)
        self['WWW-Authenticate'] = "Basic realm=\"DataGator\""
        pass

    pass
