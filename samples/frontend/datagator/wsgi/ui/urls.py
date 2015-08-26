# -*- coding: utf-8 -*-
"""
    datagator.wsgi.ui.urls
    ~~~~~~~~~~~~~~~~~~~~~~

    URL Configuration for the `DataGator`_ UI site.

    .. _`DataGator`: https://www.data-gator.com/

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.
"""

from django.conf.urls import include, patterns, url

from datagator.util.regex import VAR_REGEX, KEY_REGEX

from . import views


data_patterns = [
    # data set view
    url(r'^/?$', views.repo.dataset),
    # data item view: recipe bulder
    url(r'^/(?P<key>{0})\.recipe/?$'.format(KEY_REGEX), views.repo.recipe),
    # data item view: data explorer
    url(r'^/(?P<key>{0})/?$'.format(KEY_REGEX), views.repo.matrix),
]

repo_patterns = [
    url(r'^(?P<repo>{0})'.format(VAR_REGEX), include([
        url(r'^/?$', views.repo.dashboard, name="dashboard"),
        url(r'^/(?P<name>{0})(?:\.(?P<rev>\d+))?'.format(VAR_REGEX),
            include(data_patterns)),
    ]))
]

urlpatterns = [
    url(r'^$', views.home.cover, name="cover"),
    url(r'^login(?:/.*)?$', views.home.login),
    url(r'^logout(?:/.*)?$', views.home.logout, {'next_page': "/"}),
] + repo_patterns
