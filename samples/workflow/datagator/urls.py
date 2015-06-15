# -*- coding: utf-8 -*-
"""
    datagator.urls
    ~~~~~~~~~~~~~~

    URL Configuration for the `DataGator`_ project.

    .. _`DataGator`: https://www.data-gator.com/

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.
"""

from django.conf.urls import include, url

from django.views.generic.base import RedirectView

from .views import DataItemView


VAR_REGEX = r"[A-Za-z_]\w{0,29}"

KEY_REGEX = r"""(?:[^"/?#@\\\s]|\\["'\\]){1,128}"""


data_patterns = [
    # ^/<repo>/<dataset>(|.<rev>)/<item>.recipe
    url(r'^/(?P<key>{0}(?=\.recipe)\.recipe)(?:/|)$'.format(KEY_REGEX),
        DataItemView.as_view()),
    # ^/<repo>/<dataset>(|.<rev>)/<item>
    url(r'^/(?P<key>{0})(?:/|)$'.format(KEY_REGEX),
        DataItemView.as_view()),
]


repo_patterns = [
    # ^<repo>/...
    url(r'^(?P<repo>{0})'.format(VAR_REGEX), include([
        # ^/<repo>/<dataset>(|.<rev>)/...
        url(r'^/(?P<dataset>{0})(?:(?:\.(?P<rev>\d+))|)'.format(VAR_REGEX),
            include(data_patterns)),
    ]))
]


urlpatterns = [
    url(r'^api/(?P<api_version>v1|v2)/(?P<path_info>.*)', RedirectView.as_view(
        url="https://www.data-gator.com/api/%(api_version)s/%(path_info)s",
        permanent=False
    )),
    url(r'^(?:/|)', include(repo_patterns)),
]
