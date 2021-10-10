from autorequests import utilities


# ensures utilities are working properly
# not necessarily needed, but it can be used to help debug


def test_indent():
    assert utilities.indent("a") == "    a"
    assert utilities.indent("a", spaces=8) == "        a"


def test_uses_accepted_chars():
    assert utilities.uses_accepted_chars("a", "a")
    assert not utilities.uses_accepted_chars("a", "b")


def test_is_pythonic_name():
    assert utilities.is_pythonic_name("a")
    assert not utilities.is_pythonic_name("class")


def test_extract_cookies():
    assert utilities.extract_cookies({}) == {}
    headers = {"a": "a", "cookie": "a=1; b=1"}
    assert utilities.extract_cookies(headers) == {"a": "1", "b": "1"}
    assert "cookie" not in headers
    assert headers.get("a") == "a"


def test_compare_dicts():
    dict_one = {"a": "a"}
    dict_two = {"a": "b"}
    assert utilities.compare_dicts(dict_one, dict_two) == {}
    dict_one = {"a": "a"}
    dict_two = {"a": "a"}
    assert utilities.compare_dicts(dict_one, dict_two) == {"a": "a"}


def test_format_dict():
    assert utilities.format_dict({"a": "a"}) == '{\n    "a": "a"\n}'
    assert utilities.format_dict({"a": "a"}, variables=["a"]) == '{\n    "a": a\n}'
    assert utilities.format_dict({"a": False}) == '{\n    "a": False\n}'
    assert utilities.format_dict({"a": "False"}) == '{\n    "a": "False"\n}'


def test_written_form():
    assert utilities.written_form(0) == "zero"
    assert utilities.written_form(100) == "one_hundred"
    assert utilities.written_form(999) == "nine_hundred_and_ninety_nine"


def test_unique_name():
    assert utilities.unique_name("a", []) == "a"
    assert utilities.unique_name("a", ["a_one"]) == "a_two"
    assert utilities.unique_name("a", ["a_one", "a_two"]) == "a_three"
