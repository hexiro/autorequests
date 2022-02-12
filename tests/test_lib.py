from __future__ import annotations

from typing import Union

from autorequests.lib import URL, Parameter


def test_url() -> None:
    url: URL
    url = URL("https://username:password@httpbin.org:80/cookies;hello=world#section")
    assert url.url == str(url) == "https://username:password@httpbin.org:80/cookies;hello=world#section"
    assert url.protocol == "https"
    assert url.username == "username"
    assert url.password == "password"
    assert url.domain == "httpbin.org"
    assert url.domain_name == "httpbin"
    assert url.port == 80
    assert url.path == "/cookies;hello=world"
    assert url.fragment == "section"
    url = URL("https://username:password@www.httpbin.org/")
    assert url.url == str(url) == "https://username:password@www.httpbin.org/"
    assert url.username == "username"
    assert url.password == "password"
    assert url.subdomain == "www"
    assert url.domain == "httpbin.org"
    assert url.domain_name == "httpbin"
    assert url.port is None
    url = URL("https://httpbin.org:80/?hello=world")
    # query params removed
    assert url.url == str(url) == "https://httpbin.org:80/"
    assert url.username is None
    assert url.password is None
    assert url.domain == "httpbin.org"
    assert url.port == 80
    assert url.query == {"hello": "world"}

    for x in [
        "https://httpbin.org/",
        "https://httpbin.org:443/",
        "https://username:password@httpbin.org/",
        "https://www.httpbin.org/",
        "https://username:password@httpbin.org:443/",
        "https://username:password@www.httpbin.org/",
        "https://www.httpbin.org:443/",
    ]:
        assert str(URL(x)) == x


def test_parameter() -> None:
    assert Parameter("a").code == "a"
    assert Parameter("a", typehint=str).code == "a: str"
    assert Parameter("a", default=None).code == "a=None"
    assert Parameter("a", typehint=str, default="hello!").code == "a: str = 'hello!'"
    assert Parameter("a", typehint=Union[str, int], default=None).code == "a: typing.Union[str, int] = None"
