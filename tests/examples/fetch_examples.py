from __future__ import annotations

from autorequests.parsed import ParsedInput

fetch_examples: dict[str, ParsedInput] = {}

fetch_example_one = """fetch("https://httpbin.org/cookies", {
  "headers": {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "sec-ch-ua": "\\"Chromium\\";v=\\"94\\", \\" Not A;Brand\\";v=\\"99\\", \\"Opera GX\\";v=\\"80\\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\\"Windows\\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "cookie": "hello=world"
  },
  "referrer": "https://httpbin.org/",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": null,
  "method": "GET",
  "mode": "cors"
});"""

fetch_examples[fetch_example_one] = ParsedInput(
    method="GET",
    url="https://httpbin.org/cookies",
    headers={
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua": '"Chromium";v="94", " Not A;Brand";v="99", "Opera GX";v="80"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "referer": "https://httpbin.org/",
        "referrer-policy": "strict-origin-when-cross-origin",
    },
    cookies={"hello": "world"},
    params=None,
    data=None,
    json=None,
    files=None,
)
