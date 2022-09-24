from __future__ import annotations

from autorequests import commons

# ensures commons are working properly
# not necessarily needed, but it can be used to help debug


def test_extract_cookies() -> None:
    assert commons.extract_cookies({}) == {}
    headers = {"a": "a", "cookie": "a=1; b=1"}
    assert commons.extract_cookies(headers) == {"a": "1", "b": "1"}
    assert headers == {"a": "a"}


def test_format_dict() -> None:
    assert commons.format_json_like({"a": "a"}) == '{\n    "a": "a"\n}'
    assert commons.format_json_like({"a": False}) == '{\n    "a": False\n}'
    assert commons.format_json_like({"a": "False"}) == '{\n    "a": "False"\n}'


def test_parse_url_encoded() -> None:
    assert commons.parse_url_encoded("a=1&b=2") == {"a": "1", "b": "2"}


def test_fix_escape_chars() -> None:
    assert commons.fix_escape_chars("\\t") == "\t"
    assert commons.fix_escape_chars("\\n") == "\n"
    assert commons.fix_escape_chars("\\r\\n") == "\r\n"


def test_fix_fake_escape_chars() -> None:
    assert commons.fix_fake_escape_chars('`"') == '"'
    assert commons.fix_fake_escape_chars("\\t") == "\t"
    assert commons.fix_fake_escape_chars("\\\\t") == "\t"
