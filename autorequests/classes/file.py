import json
import re
from functools import cached_property
from pathlib import Path

from .. import regexp, utils
from ..classes import URL, Body, Method

# TODO: INHERITS FROM PATH text is cached_property
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

    @cached_property
    def fetch_match(self):
        return regexp.fetch_regexp.search(self.text)

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

        cookies = utils.cookies(headers)

        method = groups["method"]
        url = URL(groups["url"])
        body = Body(groups["body"] or "")

        return Method(method=method,
                      url=url,
                      body=body,
                      headers=headers,
                      cookies=cookies,
                      )
