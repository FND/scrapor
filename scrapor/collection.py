from .html import Page
from .util import write_file, eprint

import os


class Collection:
    """
    abstraction for pages containing multiple items, optionally across multiple
    related pages (i.e. supports auto-pagination)
    """

    item_selector = None
    __slots__ = ("entry_point",)

    def __init__(self, entry_point):
        self.entry_point = entry_point

    def items(self, _url=None):
        page = Page.retrieve(_url or self.entry_point)
        for item in page.doc.select(self.item_selector):
            yield self.item(item, page)

        try:
            next_url = self.next_page(page)
        except NotImplementedError:
            next_url = None
        if next_url:
            yield from self.items(next_url)

    def item(self, node, page):
        raise NotImplementedError

    def next_page(self, page):
        raise NotImplementedError

    def __repr__(self):
        return '<%s "%s">' % (self.__class__.__name__, self.entry_point)


class PersistentCollection(Collection):
    """
    provides a store to track known items

    NB: `item` implementation is expected to invoke `self.register(id)` for
        each item
    """

    __slots__ = ("store_path", "store", "threshold")

    def __init__(self, entry_point, store_path, threshold=None):
        super().__init__(entry_point)
        self.store_path = store_path
        self.threshold = threshold
        try:
            with open(store_path, encoding="utf-8") as fh:
                self._store = [line.strip() for line in fh]
        except FileNotFoundError:
            eprint("WARNING: `%s` not found; creating new store" % store_path)
            assert os.path.isabs(store_path), (
                    "ERROR: store path must be absolute `%s`" % store_path)
            self._store = []

    def items(self, *args, **kwargs):
        yield from super().items(*args, **kwargs)
        self.save()

    def save(self):
        store = self._store
        threshold = self.threshold
        if threshold:
            excess = len(store) - threshold
            if excess > 0:
                eprint("WARNING: dropping %d old items from store" % excess)
                self._store = store = store[excess:]
        write_file(self.store_path, "\n".join(store) + "\n")

    def register(self, item_id):
        is_new = item_id not in self._store
        if is_new:
            self._store.append(item_id)
        return is_new

    def __repr__(self):
        return '<%s "%s" `%s`>' % (self.__class__.__name__,
                self.entry_point, self.store_path)
