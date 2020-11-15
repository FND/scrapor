from .http import http_request

from bs4 import BeautifulSoup

from urllib.parse import urljoin

import re


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:79.0) Gecko/20100101 Firefox/79.0"
WHITESPACE = re.compile(r"\s+")


def href(link_node, base=None):
    uri = link_node["href"]
    return uri if base is None else urljoin(base, uri)


def text(node):
    txt = node.get_text().strip()
    return WHITESPACE.sub(" ", txt)


def expect_elements(count, selector, node):
    nodes = node.select(selector)
    actual = len(nodes)
    if actual != count:
        eprint("ERROR: expected %s occurrence(s) of `%s`, found %s" %
                (count, selector, actual))
    return nodes[0] if count == 1 else nodes


class Page:
    __slots__ = ("url", "doc")

    @classmethod
    def retrieve(cls, url, *args, **kwargs):
        res = http_request("GET", url, {
            "User-Agent": USER_AGENT,
            "Accept": "text/html"
        })
        return cls(url, res, *args, **kwargs)

    def __init__(self, url, html, *args, **kwargs):
        self.url = url
        self.doc = BeautifulSoup(html, "html.parser")


class Collection(Page):
    """
    abstraction for pages containing multiple items, optionally across multiple
    related pages (i.e. supports pagination)

    auto-pagination creates one instance per URL; if present, `store` is shared
    among instances (e.g. for abort conditions within `next_page`)
    """

    item_selector = None
    __slots__ = ("store",)

    def items(self):
        for item in self.doc.select(self.item_selector):
            yield self.item(item)

        try:
            next_url = self.next_page()
        except NotImplementedError:
            next_url = None
        if next_url:
            store = getattr(self, "store", None)
            page = self.__class__.retrieve(next_url, store)
            yield from page.items()

    def item(self, node):
        raise NotImplementedError

    def next_page(self):
        raise NotImplementedError
