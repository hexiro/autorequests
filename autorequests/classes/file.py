import json
import re
from functools import cached_property
from pathlib import Path

from .. import regexp
from ..utils import extract_cookies
from ..classes import URL, Body, Method

# Path() returns type WindowsPath or PosixPath based on os
# I could replicate their os check, but this is safer in case they change it in the future.
superclass = type(Path())


class File(superclass):
    """ handles files and the parsing of files """

    # Path isn't really meant for subclassing afaik
    # so we won't overload __init__ or __new__
    # cached_properties is the way to go

    @cached_property
    def text(self):
        return self.read_text(encoding="utf8", errors="ignore")

    @cached_property
    def method(self):
        if self.fetch_match:
            return self._method_from_fetch(self.fetch_match)
        if self.powershell_match:
            return self._method_from_powershell(self.powershell_match)

    @cached_property
    def fetch_match(self):
        return regexp.fetch_regexp.search(self.text)

    @cached_property
    def powershell_match(self):
        return regexp.powershell_regexp.search(self.text)

    # static methods
    # (for parsing)

    @staticmethod
    def _method_from_fetch(fetch: re.Match) -> Method:
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
        groups = fetch.groupdict()

        headers = json.loads(fetch["headers"])
        # referer is spelled wrong in the HTTP header
        # referrer policy is not
        referrer = groups["referrer"]
        referrer_policy = groups["referrer_policy"]
        if referrer:
            headers["referer"] = referrer
        if referrer_policy:
            headers["referrer-policy"] = referrer_policy

        cookies = extract_cookies(headers)

        method = groups["method"]
        url = URL(groups["url"])
        body = Body(groups["body"] or "")

        return Method(method=method,
                      url=url,
                      body=body,
                      headers=headers,
                      cookies=cookies,
                      )

    @staticmethod
    def _method_from_powershell(powershell: re.Match) -> Method:
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
                header = header.removeprefix("  ")
                key, value = header.split("=", maxsplit=1)
                # remove leading and trailing "s that always exist
                key = key[1:-1]
                value = value[1:-1]
                headers[key] = value

        cookies = extract_cookies(headers)

        method = powershell["method"] or "GET"
        url = URL(powershell["url"])
        body = Body(powershell["body"])

        return Method(method=method,
                      url=url,
                      body=body,
                      headers=headers,
                      cookies=cookies,
                      )
