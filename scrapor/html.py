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
    assert actual == count, ("ERROR: expected %s occurrence(s) of `%s`, found %s" %
            (count, selector, actual))
    return nodes[0] if count == 1 else nodes


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
        return '<html.%s "%s">' % (self.__class__.__name__, self.url)
