from typing import Optional, Dict, List

from ..classes import URL, Body, Method

__all__ = ("parse_powershell_to_method",)


def parse_powershell_to_method(text: str) -> Optional[Method]:
    """
    Parses a file that follows this format:
    (with some potentially being optional)

    Invoke-WebRequest -Uri <URL> `
    -Method <METHOD> `
    -Headers <HEADERS> `
    -ContentType <CONTENT-TYPE> `
    -Body <BODY>
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
