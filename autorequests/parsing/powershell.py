from __future__ import annotations

from ..lib import URL, Body, Method
from ..utilities import fix_escape_chars

__all__ = ("powershell_to_method",)


def powershell_to_method(text: str) -> Method | None:
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
    headers: dict[str, str] = {}
    cookies: dict[str, str] = {}
    method: str
    url: URL | None
    body: Body | None

    # parse escape character, `
    text = text.replace("`", "\\")
    lines: list[str] = [e.rstrip("\\") for e in text.splitlines()]

    # parse custom session
    parse_session(cookies, headers, lines)

    # parse arguments
    args = parse_args("".join(lines))
    if not args or "Uri" not in args:
        return
    url = URL(args["Uri"])
    body = Body(args.get("Body"))

    parse_headers(args, headers)
    method = headers.pop("method", args.get("Method", "GET"))

    return Method(method=method, url=url, headers=headers, cookies=cookies, body=body)


def parse_headers(args: dict[str, str], headers: dict[str, str]) -> None:
    headers_string = args["Headers"][3:-2]
    for header in headers_string.split('" "'):
        key, value = header.split('"="', maxsplit=1)
        headers[key] = fix_escape_chars(value)


def parse_session(cookies: dict[str, str], headers: dict[str, str], lines: list[str]) -> None:
    if not lines:
        return
    while lines[0].startswith("$session"):
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
            left_paren = line.rfind("(") + 1
            right_paren = line.find(")")
            # ["hello-from", "autorequests", "/", "httpbin.org"]
            strings = [x.strip('"') for x in line[left_paren:right_paren].split(", ")]
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
