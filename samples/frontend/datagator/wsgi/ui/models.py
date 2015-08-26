# -*- coding: utf-8 -*-
"""
    datagator.wsgi.ui.models
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.
"""

import collections
import json


__all__ = ['RepoRef', 'DataSetRef', 'MatrixRef', 'RecipeRef', ]


class EntityRef(collections.OrderedDict):

    def __hash__(self):
        return json.dumps(self).__hash__()

    pass


class RepoRef(EntityRef):

    def __init__(self, repo):
        super(RepoRef, self).__init__([
            ('kind', "datagator#Repo"),
            ('name', repo),
        ])
        pass

    pass


class DataSetRef(EntityRef):

    def __init__(self, repo, dataset, rev=None):
        super(DataSetRef, self).__init__([
            ('kind', "datagator#DataSet"),
            ('repo', RepoRef(repo)),
            ('name', dataset),
        ])
        try:
            rev = int(rev)
        except (TypeError, ValueError):
            pass
        else:
            self['rev'] = rev
        pass

    pass


class DataItemKey(collections.OrderedDict):

    def __init__(self, kind, key):
        super(DataItemKey, self).__init__([
            ('kind', "datagator#{0}".format(kind) if kind else None),
            ('name', key)
        ])
        pass

    pass


class DataItemRef(EntityRef):

    def __init__(self, repo, dataset, rev, key):
        super(DataItemRef, self).__init__()
        self.update(DataSetRef(repo, dataset, rev))
        self['items'] = (DataItemKey(None, key), )
        self['itemsCount'] = 1
        pass

    pass


class MatrixRef(DataItemRef):

    def __init__(self, repo, dataset, rev, key):
        super(MatrixRef, self).__init__(repo, dataset, rev, key)
        self['items'][0]['kind'] = "datagator#Matrix"
        pass

    pass


class RecipeRef(DataItemRef):

    def __init__(self, repo, dataset, rev, key):
        super(RecipeRef, self).__init__(repo, dataset, rev, key)
        self['items'][0]['kind'] = "datagator#Recipe"
        pass

    pass
