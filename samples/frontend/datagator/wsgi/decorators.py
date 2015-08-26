# -*- coding: utf-8 -*-
"""
    datagator.wsgi.decorators
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.
"""

import base64
import functools

from django.contrib.auth import authenticate, login
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse, HttpResponseForbidden

from .http import HttpResponseUnauthorized


__all__ = ['with_basic_auth', ]


def _basic_auth(request):

    if request.user.is_authenticated():
        return request

    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                user = authenticate(username=uname, password=passwd)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        return request

        raise SuspiciousOperation("Failed authentication.")

    return request


def with_basic_auth(_method=None, **options):

    if _method is not None:
        return with_basic_auth()(_method)

    allow_unauthorized = options.get("allow_unauthorized", False)

    def decorator(view):

        @functools.wraps(view)
        def wrapper(request, *args, **kwargs):

            try:
                request = _basic_auth(request)
            except SuspiciousOperation:
                return HttpResponseForbidden("Failed authentication.")

            if not allow_unauthorized and not request.user.is_authenticated():
                return HttpResponseUnauthorized("Unauthorized access.")

            return view(request, *args, **kwargs)

        return wrapper

    return decorator
