# -*- coding: utf-8 -*-
"""
    datagator.api.client.repo
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by `University of Denver <http://pardee.du.edu/>`_
    :license: Apache 2.0, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2015/01/28
"""

from __future__ import unicode_literals, with_statement

import fcntl
import io
import json
import jsonschema
import logging
import tempfile

from . import environ
from ._compat import OrderedDict, to_native, to_unicode, to_bytes, _thread
from ._entity import Entity, validated

from .data import DataItem


__all__ = ['DataSet', 'Repo', ]
__all__ = [to_native(n) for n in __all__]


SEEK_SET = getattr(io, "SEEK_SET", 0)  # py26 does not define ``SEEK_*``
SEEK_CUR = getattr(io, "SEEK_CUR", 1)
SEEK_END = getattr(io, "SEEK_END", 2)


_log = logging.getLogger(__name__)


class ChangeSet(object):

    MAX_PAYLOAD_BYTES = 2 ** 24  # 16 MB
    MAX_BUFFER_BYTES = 2 ** 21   # 2 MB

    __slots__ = ['__uri', '__lock', '__tmp', '__cnt', ]

    def __init__(self, dataset):
        if not isinstance(dataset, DataSet):
            raise TypeError("invalid dataset")
        self.__uri = dataset.uri
        super(ChangeSet, self).__init__()
        self.__lock = _thread.allocate_lock()
        self.__tmp = None
        self.__cnt = 0
        self._rewind()
        pass

    def commit(self):
        """
        commit all pending revisions to the backend service
        """
        if len(self) > 0 and self.__tmp is not None:
            self._commit()
        pass

    def _rewind(self):

        if len(self) > 0:
            raise AssertionError("cannot rewind a pending revision")
        elif self.__tmp is not None:
            _log.debug("attempting to rewind an empty revision")
            # which is unnecessary, thus the short-cut return
            return

        # lock the change set to prevent changes from other threads
        if not self.__lock.acquire(0):
            raise AssertionError("failed to lock change set")

        _log.debug("creating new revision for '{0}'".format(self.__uri))
        self.__tmp = tempfile.SpooledTemporaryFile(
            max_size=ChangeSet.MAX_BUFFER_BYTES, suffix=".DataGatorCache")
        fcntl.lockf(self.__tmp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.__cnt = 0
        self.__tmp.write(to_bytes("{"))

        pass

    def _commit(self):

        if len(self) == 0:
            _log.debug("attempting to commit an empty revision")
            # which is unnecessary, thus the short-cut return
            return
        elif not self.__lock.locked():
            raise AssertionError("commit without acquiring lock")
        elif self.__tmp is None:
            raise AssertionError("cannot commit an uninitialized revision")

        self.__tmp.write(to_bytes("}"))
        self.__tmp.flush()
        self.__tmp.seek(0, SEEK_END)

        _log.debug("committing revision")
        _log.debug("  - entries count: {0}".format(len(self)))
        _log.debug("  - payload size: {0}".format(self.__tmp.tell()))

        try:
            self.__tmp.seek(0, SEEK_SET)
            if environ.DATAGATOR_API_VERSION == "v1":
                with validated(Entity.__service__.put(
                        self.__uri, data=self.__tmp), (202, )) as r:
                    # TODO watch task for completion
                    pass
            else:
                with validated(Entity.__service__.patch(
                        self.__uri, data=self.__tmp), (202, )) as r:
                    # TODO watch task for completion
                    pass
        except Exception as e:
            _log.error(e)
            raise
        else:
            # prepare for consecutive revisions
            fcntl.lockf(self.__tmp, fcntl.LOCK_UN)
            self.__tmp.close()
            self.__tmp = None
            self.__cnt = 0
            self.__lock.release()
            self._rewind()

        pass

    def __setitem__(self, key, value):
        _log.debug("appending to revision")
        key = json.dumps(key)
        value = value.read() if hasattr(value, "read") else json.dumps(value)
        _log.debug("  - key: {0}".format(key))
        _log.debug("  - size: {0}".format(len(value)))
        # write serialized value to temporary file
        f = self.__tmp
        if len(self):
            f.write(to_bytes(", "))
        f.write(to_bytes(key))
        f.write(to_bytes(": "))
        f.write(to_bytes(value))
        self.__cnt += 1
        if f.tell() < ChangeSet.MAX_PAYLOAD_BYTES:
            return
        self._commit()

    def __len__(self):
        return self.__cnt

    def __enter__(self):
        self._rewind()
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        if isinstance(exc_value, Exception):
            pass
        else:
            self._commit()
        return False  # re-raise exception

    def __del__(self):
        try:
            if len(self) > 0:
                _log.warning("pending revision left until garbage collection")
                self._commit()
        except:
            _log.error("failed to commit pending revisions")
            raise
        pass

    pass


class DataSet(Entity):

    __slots__ = ['__name', '__repo', '__rev', '__writer', '__items_dict', ]

    def __init__(self, repo, name, rev=None):
        super(DataSet, self).__init__(self.__class__.__name__)
        self.__name = to_unicode(name)
        self.__repo = repo
        self.__rev = rev if rev != -1 else None
        self.__writer = None
        self.__items_dict = None
        _log.debug("initializing dataset '{0}'".format(self.uri))
        # when `rev` is `None`, the dataset may not exist in the backend
        # service (i.e. we are creating a new dataset).
        if rev is None:
            # validate the name locally against the schema
            try:
                Entity.__schema__.validate(self.ref)
            except jsonschema.ValidationError:
                raise AssertionError("invalid dataset name")
        # when `rev` is not `None`, the dataset is assumed to exist in the
        # backend service (i.e. we are pulling remote data for use).
        else:
            # when `rev` is -1, we always invalidate the cached dataset, and
            # pull the remote revision from the backend service.
            if rev == -1:
                self.cache = None
            remote_rev = self.cache.get("rev", None)
            assert(rev == remote_rev or rev == -1), \
                "inconsistent revision '{0}' != '{1}'".format(remote_rev, rev)
            # when invoking `self.cache`, `self.rev` is already synchronized,
            # i.e., `self.rev` is always equal to `remote_rev` at this point.
        pass

    @property
    def uri(self):
        return "{0}/{1}{2}".format(
            self.repo.name, self.name,
            ".{0}".format(self.rev) if self.rev is not None else "")

    @property
    def ref(self):
        obj = OrderedDict([
            ("kind", "datagator#DataSet"),
            ("name", self.name),
            ("repo", self.repo.ref),
        ])
        if self.rev is not None:
            obj['rev'] = self.rev
        return obj

    @property
    def name(self):
        return self.__name

    @property
    def repo(self):
        return self.__repo

    @property
    def rev(self):
        return self.__rev

    @property
    def cache(self):
        content = super(DataSet, self)._cache_getter()
        # synchronize with the remote revision upon cache overwrite
        if self.__rev is None:
            self.__rev = content.get("rev", None)
        return content

    @cache.setter
    def cache(self, data):
        super(DataSet, self)._cache_setter(data)
        self.__items_dict = None
        self.__rev = None
        pass

    @property
    def items_dict(self):
        if self.__items_dict is None:
            self.__items_dict = dict([
                (i.get("name"), i) for i in self.cache.get("items", [])])
        return self.__items_dict

    def __enter__(self):
        if self.__writer is None:
            self.__writer = ChangeSet(self)
        return self.__writer.__enter__()

    def __exit__(self, ext_type, exc_value, traceback):
        assert(self.__writer is not None), "committer not initialized"
        res = self.__writer.__exit__(ext_type, exc_value, traceback)
        self.cache = None
        self.repo.cache = None
        return res

    def __contains__(self, key):
        return key in self.items_dict

    def __getitem__(self, key):
        item = self.items_dict[key]
        if isinstance(item, dict):
            # instantiate data item and cache in `items_dict`
            kind = item.get("kind", None)
            item = DataItem(kind, self, key)
            self.items_dict[key] = item
        return item

    def __setitem__(self, key, value):
        with self as c:
            c[key] = value
        pass

    def __delitem__(self, key):
        with self as c:
            c[key] = None
        pass

    def __iter__(self):
        for key in self.items_dict:
            yield key
        pass

    def __len__(self):
        return len(self.items_dict)

    def patch(self, changes):
        """
        :param items: `dict` or sequence of key-value pairs, representing
            create / update / delete operations to be committed.
        """
        if not isinstance(changes, dict):
            changes = dict(changes)
        with self as c:
            for key, value in changes.items():
                c[key] = value
        pass

    def clear(self):
        self.patch([(key, None) for key in self])
        pass

    pass


class Repo(Entity):

    __slots__ = ['__name', ]

    def __init__(self, name, access_key=None):
        super(Repo, self).__init__(self.__class__.__name__)
        self.__name = to_unicode(name)
        if self.cache is None:
            raise AssertionError("invalid repository '{0}'".format(self.name))
        if access_key is not None:
            Entity.__service__.auth = (self.name, access_key)
        pass

    @property
    def uri(self):
        return self.name

    @property
    def name(self):
        return self.__name

    @property
    def ref(self):
        return OrderedDict([
            ("kind", "datagator#Repo"),
            ("name", self.name),
        ])

    def __contains__(self, dsname):
        try:
            # if `dsname` is not a valid name for a DataSet entity, then it is
            # guaranteed to *not* exist in the storage backend.
            ref = DataSet(self, dsname)
            # looking up `Entity.__cache__` is more preferrable than `ds.cache`
            # because the latter may trigger connection to the backend service
            if Entity.__cache__.exists(ref.uri):
                return True
            return ref.cache is not None
        except (AssertionError, RuntimeError, ):
            return False
        return False  # should NOT reach here

    def __getitem__(self, dsname):
        try:
            # always return the latested revision
            return DataSet(self, dsname, -1)
        except (AssertionError, RuntimeError, ):
            pass
        raise KeyError("invalid dataset '{0}'".format(dsname))

    def __setitem__(self, dsname, items):
        ref = None
        try:
            ref = DataSet(self, dsname)
        except (AssertionError, ):
            raise KeyError("invalid dataset name")
        # create / update dataset
        if environ.DATAGATOR_API_VERSION == "v1":
            with validated(Entity.__service__.put(self.uri, ref.ref), (202, )):
                # TODO watch task for completion
                pass
        else:
            with validated(
                    Entity.__service__.put(ref.uri, ref.ref), (200, 201)):
                # since v2, data set creation / update is a synchronized
                # operation, no task will be created whatsoever
                pass
        # commit revision(s) with the new items. `ref.patch()` will also
        # invalidate local cache for both the repo and the referenced dataset.
        ref.patch(items)
        pass

    def __delitem__(self, dsname):
        raise NotImplementedError()

    def __iter__(self):
        for ref in self.cache.get("items", []):
            yield ref.get("name")
        pass

    def __len__(self):
        return self.cache.get("itemsCount", 0)

    pass
