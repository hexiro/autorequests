from __future__ import annotations

import json
import typing as t

from ..commons import extract_cookies, parse_url
from ..request import Request
from .body import parse_body

if t.TYPE_CHECKING:
    from ..typings import JSON, Data, Files


__all__ = ("parse_fetch", "is_fetch")


def is_fetch(text: str) -> bool:
    return text.startswith("fetch(")


def parse_fetch(text: str) -> Request | None:
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
    data: Data | None
    json_: JSON | None
    files: Files | None

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
    data, json_, files = parse_body(options.get("body"), headers.get("content-type"))

    return Request(
        method=method,
        url=url,
        headers=headers,
        cookies=cookies,
        params=params,
        data=data,
        json=json_,
        files=files,
    )
