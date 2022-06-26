from __future__ import annotations

import urllib.parse

from .commons import parse_url_encoded


def parse_url(url: str) -> tuple[str, dict[str, str] | None]:
    parsed_url = urllib.parse.urlparse(url)
    query = parse_url_encoded(parsed_url.query) or None

    without_query = urllib.parse.ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, "", parsed_url.fragment
    )

    return without_query.geturl(), query
