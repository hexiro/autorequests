from __future__ import annotations

from autorequests.request import Request

httpbin_examples: dict[str, Request] = {}

httpbin_method_delete_fetch = """fetch("http://httpbin.org/delete", {
  "headers": {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "Referer": "http://httpbin.org/",
    "Referrer-Policy": "strict-origin-when-cross-origin"
  },
  "body": null,
  "method": "DELETE"
});"""

httpbin_method_delete_powershell = """$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 OPR/90.0.4480.100"
Invoke-WebRequest -UseBasicParsing -Uri "http://httpbin.org/delete" `
-Method "DELETE" `
-WebSession $session `
-Headers @{
"Accept-Encoding"="gzip, deflate"
  "Accept-Language"="en-US,en;q=0.9"
  "Origin"="http://httpbin.org"
  "Referer"="http://httpbin.org/"
  "accept"="application/json"
}"""

httpbin_method_delete_fetch_request = Request(
    method="DELETE",
    url="http://httpbin.org/delete",
    headers={
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "Referer": "http://httpbin.org/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    },
    cookies=None,
    params=None,
    json=None,
    data=None,
    files=None,
)


httpbin_method_delete_powershell_request = Request(
    method="DELETE",
    url="http://httpbin.org/delete",
    headers={
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "http://httpbin.org",
        "Referer": "http://httpbin.org/",
        "accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 OPR/90.0.4480.100",
    },
    cookies=None,
    params=None,
    json=None,
    data=None,
    files=None,
)

httpbin_examples[httpbin_method_delete_fetch] = httpbin_method_delete_fetch_request
httpbin_examples[httpbin_method_delete_powershell] = httpbin_method_delete_powershell_request
