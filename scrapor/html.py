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
        return '<html.Collection "%s">' % self.entry_point


class Page:
    __slots__ = ("url", "doc")

    @classmethod
    def retrieve(cls, url):
        res = http_request("GET", url, {
            "User-Agent": USER_AGENT,
            "Accept": "text/html"
        })
        return cls(url, res)

    def __init__(self, url, html):
        self.url = url
        self.doc = BeautifulSoup(html, "html.parser")

    def __repr__(self):
        return '<html.Page "%s">' % self.url
