import json
from typing import Match

from .. import regexp
from ..classes import URL, Body, Method
from ..utils import extract_cookies, PathType


class File(PathType):
    """ handles files and the parsing of files """

    def __new__(cls, *args):
        return super().__new__(cls, *args)

    def __init__(self, *args):
        super().__init__()
        # *args is needed but not used
        self.__text = self.read_text(encoding="utf8", errors="ignore")
        self.__method = self._compute_method()

    @property
    def text(self):
        return self.__text

    @property
    def method(self):
        return self.__method

    def _compute_method(self):
        fetch = self.fetch_match
        if fetch:
            return self._method_from_fetch(fetch)
        powershell = self.powershell_match
        if powershell:
            return self._method_from_powershell(powershell)

    @property
    def fetch_match(self):
        return regexp.fetch_regexp.search(self.text)

    @property
    def powershell_match(self):
        return regexp.powershell_regexp.search(self.text)

    # static methods
    # (for parsing)

    @staticmethod
    def _method_from_fetch(fetch: Match) -> Method:
        """
        Parses a file that follows this format:

        fetch(<URL>, {
          "headers": <HEADERS>,
          "referrer": <REFERRER>,  # optional
          "referrerPolicy": <REFERRER-POLICY>,  # might be optional
          "body": <BODY>,
          "method": <METHOD>,
          "mode": <MODE>
        });
        """
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

    @staticmethod
    def _method_from_powershell(powershell: Match) -> Method:
        """
        Parses a file that follows this format:

        Invoke-WebRequest -Uri <URL> `
        -Method <METHOD> `   # optional; defaults to GET if not set
        -Headers <HEADERS> `
        -ContentType <CONTENT-TYPE> `   # optional; only exists w/ body
        -Body <BODY>     # optional; only exists if a body is present
        """
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
