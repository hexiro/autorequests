from __future__ import annotations

import json
import urllib.parse


def extract_cookies(headers: dict[str, str]) -> dict[str, str]:
    """:returns: a dict of cookies based off the 'cookie' header"""
    cookie_header = headers.pop("cookie", None)
    if not cookie_header:
        return {}
    cookie_dict = {}
    for cookie in cookie_header.split("; "):
        key, value = cookie.split("=", maxsplit=1)
        cookie_dict[key] = value
    return cookie_dict


def format_dict(data: dict, indent: int | None = 4) -> str:
    """format a dictionary"""
    # I'm not sure it's possible to pretty-format this with something like
    # pprint, but if it is possible LMK!
    formatted = json.dumps(data, indent=indent)
    # parse bools and none
    # leading space allows us to only match literal false and not "false" string
    formatted = formatted.replace(" null", " None")
    formatted = formatted.replace(" true", " True")
    formatted = formatted.replace(" false", " False")
    return formatted


def format_string(text: str) -> str:
    """formats a string"""
    if "'" in text or '"' in text:
        # text contains a quote, so let python escape it optimally
        return repr(text)
    # double quotes by default
    return f'"{text}"'


def parse_url_encoded(x: str) -> dict[str, str]:
    """parses application/x-www-form-urlencoded and query string params"""
    return dict(urllib.parse.parse_qsl(x, keep_blank_values=True))


def fix_escape_chars(body: str) -> str:
    """
    replaces escaped \\ followed by a letter to the appropriate char
    (ex. "\\t" --> "\t")
    """
    return body.encode(encoding="utf8", errors="ignore").decode(encoding="unicode_escape", errors="ignore")


def fix_fake_escape_chars(body: str) -> str:
    """
    replaces powershell's ` escape char with fake python escape chars and then
    fixes the fake escape chars twice to not only fix the fake ones we added, but the fake ones that powershell added.
    * could do with improvement in the future.
    (ex. "`\"" --> "\"")
    (ex. "\\t" --> "\t")
    """
    return fix_escape_chars(fix_escape_chars(body.replace("`", "\\")))
