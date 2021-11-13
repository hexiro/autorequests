import json
from typing import Optional

from ..lib import Method, URL, Body
from ..utilities import extract_cookies

__all__ = ("fetch_to_method",)


def fetch_to_method(text: str) -> Optional[Method]:
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
