from __future__ import annotations

from autorequests import utilities


# ensures utilities are working properly
# not necessarily needed, but it can be used to help debug


def test_indent() -> None:
    assert utilities.indent("a") == "    a"
    assert utilities.indent("a", spaces=8) == "        a"
    assert utilities.indent("a\n\na") == "    a\n\n    a"


def test_is_pythonic_name() -> None:
    assert utilities.is_pythonic_name("a")
    assert not utilities.is_pythonic_name("class")
    assert not utilities.is_pythonic_name("0a")


def test_extract_cookies() -> None:
    assert utilities.extract_cookies({}) == {}
    headers = {"a": "a", "cookie": "a=1; b=1"}
    assert utilities.extract_cookies(headers) == {"a": "1", "b": "1"}
    assert headers == {"a": "a"}


def test_compare_dicts() -> None:
    dict_one = {"a": "a"}
    dict_two = {"a": "b"}
    assert utilities.merge_dicts(dict_one, dict_two) == {}
    dict_one = {"a": "a"}
    dict_two = {"a": "a"}
    assert utilities.merge_dicts(dict_one, dict_two) == {"a": "a"}


def test_format_dict() -> None:
    assert utilities.format_dict({"a": "a"}) == '{\n    "a": "a"\n}'
    assert utilities.format_dict({"a": "a"}, variables=["a"]) == '{\n    "a": a\n}'
    assert utilities.format_dict({"a": False}) == '{\n    "a": False\n}'
    assert utilities.format_dict({"a": "False"}) == '{\n    "a": "False"\n}'


def test_parse_url_encoded() -> None:
    assert utilities.parse_url_encoded("a=1&b=2") == {"a": "1", "b": "2"}


def test_written_form() -> None:
    assert utilities.written_form(0) == "zero"
    assert utilities.written_form(10) == "ten"
    assert utilities.written_form(11) == "eleven"
    assert utilities.written_form(15) == "fifteen"
    assert utilities.written_form(100) == "one_hundred"
    assert utilities.written_form(999) == "nine_hundred_and_ninety_nine"
    assert utilities.written_form(999) == utilities.written_form("999")
    assert utilities.written_form("999abcdefbh") == "nine_hundred_and_ninety_nine_abcdefbh"
    assert utilities.written_form("abcdefbh") == "abcdefbh"


def test_unique_name() -> None:
    assert utilities.unique_name("a", []) == "a"
    assert utilities.unique_name("a", ["a_one"]) == "a_two"
    assert utilities.unique_name("a", ["a_one", "a_two"]) == "a_three"


def test_fix_escape_chars() -> None:
    assert utilities.fix_escape_chars("\\t") == "\t"
    assert utilities.fix_escape_chars("\\n") == "\n"
    assert utilities.fix_escape_chars("\\r\\n") == "\r\n"
