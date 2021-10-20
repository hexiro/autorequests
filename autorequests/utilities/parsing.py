import json
from typing import Optional, Dict, List

from . import extract_cookies
from ..classes import Method, URL, Body


def method_from_text(text: str) -> Optional[Method]:  # type: ignore
    # short circuiting
    if text:
        return method_from_fetch(text) or method_from_powershell(text)


def method_from_fetch(text: str) -> Optional[Method]:
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
    signature_split = text.split("\"")

    if len(signature_split) < 3:
        return

    if signature_split[0] != "fetch(":
        return

    url = URL(signature_split[1])

    if not signature_split[2].startswith(","):
        # no options specified -- should never be reached
        return

    left_brace = text.find("{")
    right_brace = text.rfind("}") + 1

    options = json.loads(text[left_brace:right_brace])

    headers = options["headers"]
    # referer is spelled wrong in the HTTP header
    # referrer policy is not
    referrer = options.get("referrer")
    referrer_policy = options.get("referrerPolicy")
    if referrer:
        headers["referer"] = referrer
    if referrer_policy:
        headers["referrer-policy"] = referrer_policy

    cookies = extract_cookies(headers)

    method = options["method"]
    body = Body(options["body"])

    return Method(method=method,
                  url=url,
                  body=body,
                  headers=headers,
                  cookies=cookies,
                  )


def method_from_powershell(text: str) -> Optional[Method]:
    """
    Parses a file that follows this format:
    (with some potentially being optional)

    Invoke-WebRequest -Uri <URL> `
    -Method <METHOD> `   # optional; defaults to GET if not set
    -Headers <HEADERS> `
    -ContentType <CONTENT-TYPE> `   # optional; only exists w/ body
    -Body <BODY>     # optional; only exists if a body is present
    """
    headers: Dict[str, str] = {}
    cookies: Dict[str, str] = {}
    method: str = "GET"
    url: Optional[URL]
    body: Optional[Body]

    # parse escape character, `
    text = text.replace("`", "\\")
    lines: List[str] = [e.rstrip("\\") for e in text.splitlines()]

    # parse custom session
    parse_session(cookies, headers, lines)

    # parse arguments
    args = parse_args("".join(lines))
    url = URL(args["Uri"])
    body = Body(args.get("Body"))

    parse_headers(args, headers)
    headers.pop("method", None)

    return Method(method=method,
                  url=url,
                  headers=headers,
                  cookies=cookies,
                  body=body
                  )


def parse_headers(args, headers):
    headers_string = args["Headers"][3:-2]
    for header in headers_string.split("\" \""):
        key, value = header.split("\"=\"", maxsplit=1)
        headers[key] = value


def parse_session(cookies, headers, lines):
    while lines[0].startswith("$session"):
        line = lines.pop(0)
        if line.startswith("$session.UserAgent"):
            # $session.UserAgent = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en) AppleWebKit (KHTML, like Gecko)"
            headers["User-Agent"] = line.split("\"")[1]
        elif line.startswith("$session.Cookies.Add"):
            # $session.Cookies.Add((New-Object System.Net.Cookie("hello-from", "autorequests", "/", "httpbin.org")))
            # System.Net.Cookie("hello-from", "autorequests", "/", "httpbin.org")
            #                       Name         Value       Path     Domain
            # reference: https://docs.microsoft.com/en-us/dotnet/api/system.net.cookie?view=net-5.0#constructors
            # path and domain will be ignored because that logic is handled elsewhere
            left_paren = line.rfind("(") + 1
            right_paren = line.find(")")
            # ["hello-from", "autorequests", "/", "httpbin.org"]
            strings = [x.strip("\"") for x in line[left_paren:right_paren].split(", ")]
            name, value = strings[:2]
            cookies[name] = value


def parse_args(line: str):
    args: Dict[str, str] = {}

    line_split: List[str] = line.split()

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
        if value.startswith("\"") and value.endswith("\""):
            value = value[1:-1]
        args[key] = value

    return args
