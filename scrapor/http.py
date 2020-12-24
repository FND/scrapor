from .lui import lui

from urllib.parse import urlparse
from http import client


CLIENTS = {
    "http": client.HTTPConnection,
    "https": client.HTTPSConnection
}


def http_request(method, url, headers={}, body=None):
    lui.print("retrieving <%s>..." % url)
    url = urlparse(url)
    uri = "?".join([x for x in [url.path, url.query] if x]) # TODO: `url.params`?
    conn = CLIENTS[url.scheme](url.netloc)

    conn.request(method, uri, headers=headers, body=body) # TODO: support for redirects
    return conn.getresponse()


def fully_qualified(uri):
    return uri.startswith("http://") or uri.startswith("https://")
