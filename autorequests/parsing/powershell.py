from __future__ import annotations

import re
import typing as t
from collections import defaultdict

from ..commons import fix_escape_chars, fix_fake_escape_chars, parse_url
from ..request import Request
from .body import parse_body

if t.TYPE_CHECKING:
    from ..typings import JSON, Data, Files


__all__ = ("parse_powershell", "is_powershell")


def is_powershell(text: str) -> bool:
    return text.startswith("$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession")


def parse_powershell(text: str) -> Request | None:
    """
    Parses a file that follows this format:
    (with some parts being optional)

    $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $session.UserAgent = <USER-AGENT>
    $session.Cookies.Add(<COOKIE>)
    Invoke-WebRequest -Uri <URL> `
    -Method <METHOD> `
    -Headers <HEADERS> `
    -ContentType <CONTENT-TYPE> `
    -Body <BODY>
    """
    method: str
    url: str
    headers: dict[str, str] = {}
    cookies: dict[str, str] = {}
    params: dict[str, str] | None
    data: Data | None = None
    json_: JSON | None = None
    files: Files | None = None

    # parse escape character, `
    text = text.replace("`", "\\")
    lines: list[str] = [e.rstrip("\\") for e in text.splitlines()]

    # parse custom session
    parse_session(lines, headers, cookies)

    # parse arguments
    args = parse_args("".join(lines))

    if not args or ("Uri" not in args) or ("WebSession" not in args) or ("Headers" not in args):
        return None
    if not args["Headers"].startswith("@{") or not args["Headers"].endswith("}"):
        return None

    url, params = parse_url(args["Uri"])
    body = args.get("Body")

    if body:
        body = pre_parse_body(body)
        data, json_, files = parse_body(body, args.get("ContentType"))

    parse_headers(args, headers)
    method = headers.pop("method", args.get("Method", "GET"))

    return Request(
        method=method,
        url=url,
        headers=headers,
        cookies=cookies,
        params=params,
        data=data,
        json=json_,
        files=files,
    )


def parse_session(lines: list[str], headers: dict[str, str], cookies: dict[str, str]) -> None:
    while lines and lines[0].startswith("$session"):
        line = lines.pop(0)
        if line.startswith("$session.UserAgent"):
            # $session.UserAgent = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en) AppleWebKit (KHTML, like Gecko)"
            headers["user-agent"] = line.split('"')[1]
        elif line.startswith("$session.Cookies.Add"):
            # $session.Cookies.Add((New-Object System.Net.Cookie("hello-from", "autorequests", "/", "httpbin.org")))
            # System.Net.Cookie("hello-from", "autorequests", "/", "httpbin.org")
            #                       Name         Value       Path     Domain
            # reference: https://docs.microsoft.com/en-us/dotnet/api/system.net.cookie?view=net-5.0#constructors
            # path and domain will be ignored because that logic is handled elsewhere
            left_paren = line.rfind("(")
            right_paren = line.find(")")
            # ["hello-from", "autorequests", "/", "httpbin.org"]
            strings = [fix_fake_escape_chars(x[1:-1]) for x in line[left_paren + 1 : right_paren].split(", ")]
            name, value = strings[:2]
            cookies[name] = value


def parse_args(text: str) -> dict[str, str]:
    args: dict[str, str] = defaultdict(str)
    text_split: list[str] = text.split()

    # find all possible cli args
    regex = re.compile(r"(?:[\n\r ]\-(?P<name>[a-zA-Z]+))")
    keys: set[str] = set(x.group("name") for x in regex.finditer(text))

    key: str = ""

    while text_split:
        section = text_split.pop(0)

        if section.startswith("-"):
            possible_key = section.lstrip("-")
            if possible_key in keys:
                key = possible_key
        elif key and not section.isspace():
            args[key] += f" {section}"

    for key, value in args.items():
        value = value.lstrip()
        value = value.strip('"')
        args[key] = value

    return args


def parse_headers(args: dict[str, str], headers: dict[str, str]) -> None:
    headers_string = args["Headers"][3:-2]
    for header in headers_string.split('" "'):
        try:
            key, value = header.split('"="', maxsplit=1)
            headers[key] = fix_escape_chars(value)
        except ValueError:
            continue


def pre_parse_body(body: str) -> str:
    """
    Pre-parse the body to de-powershell the characters.
    ex: `$([char]13)` -> "\r"
    """

    if not body.startswith("([System.Text.Encoding]::UTF8.GetBytes("):
        return body

    left_quote = body.find('"')
    right_quote = body.rfind('"')

    if left_quote == -1 or right_quote == -1:
        return body

    final_data: str = ""
    quoted_data = body[left_quote + 1 : right_quote]

    for part in quoted_data.split("$"):
        if not part.startswith("([char]"):
            final_data += part
            continue

        right_paren = part.find(")")
        ordinal, rest = part[0 : right_paren + 1], part[right_paren + 1 :]

        # remove the `$([char]` from beg and `)` from end
        ordinal = ordinal[7:-1]
        ordinal_int = int(ordinal)

        final_data += chr(ordinal_int) + rest

    return final_data
