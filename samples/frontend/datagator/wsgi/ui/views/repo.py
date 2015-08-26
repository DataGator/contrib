# -*- coding: utf-8 -*-
"""
    datagator.wsgi.ui.views.repo
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.
"""

import json

from django.template.response import TemplateResponse

from ..models import RepoRef, DataSetRef, MatrixRef, RecipeRef

__all__ = ['dashboard', 'dataset', 'recipe', 'matrix', ]


DATAGATOR_API_URL = "https://www.data-gator.com/api/v2/"


def dashboard(request, repo):

    context = {
        'api_url': DATAGATOR_API_URL,
        'entity_ref': json.dumps(RepoRef(repo), indent=4)
    }

    if request.user.get_username() != repo:
        # third-party (visitor) view of the repository
        return TemplateResponse(request, "dashboard_3pty.html", context)

    # first-party (owner) view of the repository
    return TemplateResponse(request, "dashboard.html", context)


def dataset(request, repo, name, rev=None):

    context = {
        'api_url': DATAGATOR_API_URL,
        'entity_ref': json.dumps(DataSetRef(repo, name), indent=4)
    }

    return TemplateResponse(request, "dataset.html", context)


def recipe(request, repo, name, rev, key):

    context = {
        'api_url': DATAGATOR_API_URL,
        'entity_ref': json.dumps(RecipeRef(repo, name, rev, key), indent=4)
    }

    return TemplateResponse(request, "recipe.html", context)


def matrix(request, repo, name, rev, key):

    context = {
        'api_url': DATAGATOR_API_URL,
        'entity_ref': json.dumps(MatrixRef(repo, name, rev, key), indent=4)
    }

    return TemplateResponse(request, "matrix.html", context)
