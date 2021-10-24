from typing import Optional

from autorequests.lib import URL, Parameter


def test_url():
    url_one = URL("https://username:password@httpbin.org:80/cookies;hello=world#section")
    assert url_one.url == "https://username:password@httpbin.org:80/cookies;hello=world#section"
    assert str(url_one) == "https://username:password@httpbin.org:80/cookies;hello=world#section"
    assert url_one.protocol == "https"
    assert url_one.username == "username"
    assert url_one.password == "password"
    assert url_one.domain == "httpbin.org"
    assert url_one.port == 80
    assert url_one.path == "/cookies;hello=world"
    assert url_one.fragment == "section"
    url_two = URL("https://username:password@httpbin.org/")
    assert url_two.username == "username"
    assert url_two.password == "password"
    assert url_two.domain == "httpbin.org"
    assert url_two.port is None
    url_three = URL("https://httpbin.org:80/")
    assert url_three.username is None
    assert url_three.password is None
    assert url_three.domain == "httpbin.org"
    assert url_three.port == 80


def test_parameter():
    assert Parameter("what").code == "what"
    assert Parameter("what", typehint=str).code == "what: str"
    assert Parameter("what", default=None).code == "what=None"
    assert Parameter("what", typehint=str, default="hello!").code == "what: str = 'hello!'"
    assert Parameter("what", typehint=Optional[str], default=None).code == "what: typing.Optional[str] = None"
