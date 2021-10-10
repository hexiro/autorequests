import json
from typing import Optional

from . import regexp
from autorequests.classes import Method, URL, Body
from . import extract_cookies


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
    fetch = regexp.fetch_regexp.search(text)
    if not fetch:
        return  # type: ignore

    headers = json.loads(fetch["headers"])
    # referer is spelled wrong in the HTTP header
    # referrer policy is not
    referrer = fetch["referrer"]
    referrer_policy = fetch["referrer_policy"]
    if referrer:
        headers["referer"] = referrer
    if referrer_policy:
        headers["referrer-policy"] = referrer_policy

    cookies = extract_cookies(headers)

    method = fetch["method"]
    url = URL(fetch["url"])
    body = Body(fetch["body"])

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
    powershell = regexp.powershell_regexp.search(text)
    if not powershell:
        return  # type: ignore

    headers = {}
    for header in powershell["headers"].splitlines():
        if "=" in header:
            header = header.lstrip("  ")
            key, value = header.split("=", maxsplit=1)
            # remove leading and trailing "s that always exist
            key = key[1:-1]
            value = value[1:-1]
            headers[key] = value

    cookies = extract_cookies(headers)

    # ` is the escape character in powershell
    # replace two `s with a singular `
    # replace singular `s with nothing

    raw_body = powershell["body"]
    if raw_body:
        raw_body = "".join((e if e != "" else "`") for e in raw_body.split("`"))

    method = powershell["method"] or "GET"
    url = URL(powershell["url"])
    body = Body(raw_body)

    return Method(method=method,
                  url=url,
                  body=body,
                  headers=headers,
                  cookies=cookies,
                  )
