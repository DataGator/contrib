# -*- coding: utf-8 -*-
"""
    datagator.rest.decorators
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.
"""

import base64

from django.contrib.auth import authenticate, login
from django.core.exceptions import SuspiciousOperation

__all__ = ['with_authentication', ]


def _basic_auth(request):

    if request.user.is_authenticated():
        return request

    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':', 1)
                user = authenticate(username=uname, password=passwd)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        return request

        raise SuspiciousOperation("Failed authentication.")

    return request


def with_authentication(_method=None, **options):

    if _method is not None:
        return with_authentication()(_method)

    allow_unauthorized = options.get("allow_unauthorized", False)

    def decorator(method):

        @functools.wraps(method)
        def wrapper(view, request, *args, **kwargs):

            # user is already authenticated
            try:
                request = _basic_auth(request)
            except SuspiciousOperation:
                # user-submitted authorization header cannot be authenticated
                return MessageResponse(403, "Failed authentication.")

            if not allow_unauthorized and not request.user.is_authenticated():
                response = MessageResponse(401, "Unauthorized access.")
                response['WWW-Authenticate'] = "Basic realm=\"DataGator\""
                return response

            return method(view, request, *args, **kwargs)

        return wrapper

    return decorator
