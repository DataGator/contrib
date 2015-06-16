# -*- coding: utf-8 -*-
"""
    datagator.views
    ~~~~~~~~~~~~~~~

    URL Configuration for the `DataGator`_ project.

    .. _`DataGator`: https://www.data-gator.com/

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.
"""

import json

from django.shortcuts import render
from django.views.generic.base import View


class WorkFlowView(View):

    kind = None

    def get(self, request, repo, dataset, rev, key):

        cookbook = {
            'api_url': "https://www.data-gator.com/api/v1/",
            'entity_ref': json.dumps({
                'repo': {
                    'kind': "datagator#Repo",
                    'name': repo
                },
                'name': dataset,
                'rev': rev,
                'items': [{
                    'kind': self.kind,
                    'name': key
                }],
                'itemsCount': 1
            }, indent=4),
        }

        return render(request, "workflow.html", cookbook)

    pass
