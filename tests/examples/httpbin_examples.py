from __future__ import annotations

httpbin_example_one = """fetch("http://httpbin.org/ip", {
  "headers": {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "Referer": "http://httpbin.org/",
    "Referrer-Policy": "strict-origin-when-cross-origin"
  },
  "body": null,
  "method": "GET"
});"""
