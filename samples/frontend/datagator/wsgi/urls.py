# -*- coding: utf-8 -*-
"""
    datagator.wsgi.urls
    ~~~~~~~~~~~~~~~~~~~

    URL Configuration for the `DataGator`_ project.

    .. _`DataGator`: https://www.data-gator.com/

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.
"""

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

from . import ui

api_patterns = [
    url(r'^(?P<api_version>v1|v2)/(?P<path_info>.*)', RedirectView.as_view(
        url="https://www.data-gator.com/api/%(api_version)s/%(path_info)s",
        permanent=False
    )),
]

urlpatterns = [
    url(r'^api/', include(api_patterns, namespace="api")),
    url(r'^admin$', RedirectView.as_view(url="/admin/", permanent=False)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^/?', include(ui.urls, namespace="ui")),
]
