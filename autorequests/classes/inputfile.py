import json
from typing import Optional

from .. import regexp
from ..classes import URL, Body, Method
from ..utils import extract_cookies, PathType, cached_property


class InputFile(PathType):
    """ handles files and the parsing of files """

    @cached_property
    def text(self):
        return self.read_text(encoding="utf8", errors="ignore")

    @cached_property
    def method(self) -> Optional[Method]:
        # short circuiting
        return self.method_from_fetch or self.method_from_powershell

    # static methods
    # (for parsing)

    @cached_property
    def method_from_fetch(self) -> Optional[Method]:
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
        fetch = regexp.fetch_regexp.search(self.text)
        if not fetch:
            return

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

    @cached_property
    def method_from_powershell(self) -> Optional[Method]:
        """
        Parses a file that follows this format:
        (with some potentially being optional)

        Invoke-WebRequest -Uri <URL> `
        -Method <METHOD> `   # optional; defaults to GET if not set
        -Headers <HEADERS> `
        -ContentType <CONTENT-TYPE> `   # optional; only exists w/ body
        -Body <BODY>     # optional; only exists if a body is present
        """
        powershell = regexp.powershell_regexp.search(self.text)
        if not powershell:
            return

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
            raw_body = raw_body.split("`")
            raw_body = "".join((e if e != "" else "`") for e in raw_body)

        method = powershell["method"] or "GET"
        url = URL(powershell["url"])
        body = Body(raw_body)

        return Method(method=method,
                      url=url,
                      body=body,
                      headers=headers,
                      cookies=cookies,
                      )
