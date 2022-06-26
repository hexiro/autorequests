"""Handles the parsing of the raw browser input"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

from .body import parse_body
from .url import parse_url
from .commons import extract_cookies, fix_escape_chars, fix_fake_escape_chars
from .parsed import ParsedInput

if TYPE_CHECKING:
    from .typings import JSON, Data, Files


def parse_input(text: str) -> ParsedInput | None:
    return parse_fetch(text) or parse_powershell(text)


def parse_fetch(text: str) -> ParsedInput | None:
    """
    Parses a file that follows this format:
    (with some being optional)

    fetch(<URL>, {
      "headers": <HEADERS>,
      "referrer": <REFERRER>,
      "referrerPolicy": <REFERRER-POLICY>,
      "body": <BODY>,
      "method": <METHOD>,
      "mode": <MODE>
    });
    """
    method: str
    url: str
    headers: dict[str, str] | None  # type: ignore
    cookies: dict[str, str] | None
    params: dict[str, str] | None
    data: Data | None
    json_: JSON | None
    files: Files | None

    signature_split = text.split('"')

    if len(signature_split) < 3:
        return

    if signature_split[0] != "fetch(":
        return

    url, params = parse_url(signature_split[1])

    if not signature_split[2].startswith(","):
        # no options specified -- should never be reached
        return

    left_brace = text.find("{")
    right_brace = text.rfind("}") + 1

    options = json.loads(text[left_brace:right_brace])

    headers: dict[str, str] = options["headers"]
    # referer is spelled wrong in the HTTP header
    # referrer policy is not
    referrer = options.get("referrer")
    referrer_policy = options.get("referrerPolicy")
    if referrer:
        headers["referer"] = referrer
    if referrer_policy:
        headers["referrer-policy"] = referrer_policy

    cookies = extract_cookies(headers)

    method = options.get("method", "GET")
    data, json_, files = parse_body(options.get("body"))

    return ParsedInput(
        method=method,
        url=url,
        headers=headers,
        cookies=cookies,
        params=params,
        data=data,
        json=json_,
        files=files,
    )


def parse_powershell(text: str) -> ParsedInput | None:
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
    data: Data | None
    json_: JSON | None
    files: Files | None

    def parse_session() -> None:
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

    def parse_args(line: str) -> dict[str, str]:
        args: dict[str, str] = {}
        line_split: list[str] = line.split()

        def last_key() -> str:
            return list(args.keys())[-1]

        while line_split:
            line = line_split.pop(0)
            if line.startswith("-"):
                arg = line.lstrip("-")
                args[arg] = ""
            elif args and not line.isspace():
                key = last_key()
                args[key] = f"{args[key]} {line}"

        for key, value in args.items():
            value = value.lstrip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            args[key] = value

        return args

    def parse_headers() -> None:
        headers_string = args["Headers"][3:-2]
        for header in headers_string.split('" "'):
            key, value = header.split('"="', maxsplit=1)
            headers[key] = fix_escape_chars(value)

    # parse escape character, `
    text = text.replace("`", "\\")
    lines: list[str] = [e.rstrip("\\") for e in text.splitlines()]

    # parse custom session
    parse_session()

    # parse arguments
    args = parse_args("".join(lines))

    print(args)
    print()
    print(args["Headers"])
    print()

    if not args or "Uri" not in args:
        return

    url, params = parse_url(args["Uri"])
    data, json_, files = parse_body(args.get("Body"))

    parse_headers()
    method = headers.pop("method", args.get("Method", "GET"))

    return ParsedInput(
        method=method,
        url=url,
        headers=headers,
        cookies=cookies,
        params=params,
        data=data,
        json=json_,
        files=files,
    )
