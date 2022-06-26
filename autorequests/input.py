import json


from .body import parse_body
from .url import parse_url
from .commons import extract_cookies
from .parsed import ParsedInput


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
    data: dict[str, str] | None
    json_: dict[str, str] | None
    files: dict[str, tuple[str, ...]] | None

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
    data: dict[str, str] | None
    json_: dict[str, str] | None
    files: dict[str, tuple[str, ...]] | None

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
                strings = [x[1:-1] for x in line[left_paren + 1 : right_paren].split(", ")]
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

    def parse_headers() -> dict[str, str]:
        headers_string = args["Headers"][1:].replace('" "', '", "').replace('"="', '": "') + "}"
        headers = json.loads(headers_string)
        return headers

    # parse escape character, `
    text = text.replace("`", "\\")
    lines: list[str] = [e.rstrip("\\") for e in text.splitlines()]

    # parse custom session
    parse_session()

    # parse arguments
    args = parse_args("".join(lines))

    if not args or "Uri" not in args:
        return

    url, params = parse_url(args["Uri"])
    data, json_, files = parse_body(args.get("Body"))

    headers = parse_headers()
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
