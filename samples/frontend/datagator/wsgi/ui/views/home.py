# -*- coding: utf-8 -*-
"""
    datagator.wsgi.ui.views.home
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.
"""

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, resolve_url
from django.template.response import TemplateResponse
from django.views.decorators import cache, csrf
from django.contrib.auth import logout as auth_logout

from datagator.wsgi.decorators import with_basic_auth


__all__ = ['cover', 'login', 'logout', ]


def cover(request):

    context = {}

    return TemplateResponse(request, "cover.html", context)


@csrf.csrf_protect
@cache.never_cache
@with_basic_auth(allow_unauthorized=True)
def login(request):

    if not request.user.is_authenticated():
        # prompt the login form for the user to post username + password
        context = {}
        return TemplateResponse(request, "login.html", context)

    redirect_uri = reverse("ui:dashboard", kwargs={
        'repo': request.user.get_username()})

    redirect_uri = request.POST.get("next_page", request.GET.get(
        "next_page", redirect_uri))

    return HttpResponseRedirect(redirect_uri)


def logout(request, next_page=None):

    auth_logout(request)

    if next_page is not None:
        next_page = resolve_url(next_page)

    return HttpResponseRedirect(next_page or reverse("ui:cover"))
