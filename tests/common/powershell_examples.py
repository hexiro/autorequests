from __future__ import annotations

from autorequests.lib import Method, URL, Body

powershell_samples: dict[str, Method] = {}

powershell_example_one = """$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 OPR/80.0.4170.48"
$session.Cookies.Add((New-Object System.Net.Cookie("hello-from", "autorequests", "/", "httpbin.org")))
Invoke-WebRequest -UseBasicParsing -Uri "https://httpbin.org/cookies" `
-WebSession $session `
-Headers @{
"method"="GET"
  "authority"="httpbin.org"
  "scheme"="https"
  "path"="/cookies"
  "sec-ch-ua"="`"Chromium`";v=`"94`", `" Not A;Brand`";v=`"99`", `"Opera GX`";v=`"80`""
  "accept"="application/json"
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"Windows`""
  "sec-fetch-site"="same-origin"
  "sec-fetch-mode"="cors"
  "sec-fetch-dest"="empty"
  "referer"="https://httpbin.org/"
  "accept-encoding"="gzip, deflate, br"
  "accept-language"="en-US,en;q=0.9"
}"""

powershell_samples[powershell_example_one] = Method(
    method="GET",
    body=Body(),
    url=URL("https://httpbin.org/cookies"),
    parameters=None,
    cookies={"hello-from": "autorequests"},
    headers={
        "authority": "httpbin.org",
        "scheme": "https",
        "path": "/cookies",
        "sec-ch-ua": '"Chromium";v="94", " Not A;Brand";v="99", "Opera GX";v="80"',
        "accept": "application/json",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://httpbin.org/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 OPR/80.0.4170.48",
    },
)

powershell_example_two = '''$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 OPR/80.0.4170.48"
Invoke-WebRequest -UseBasicParsing -Uri "https://dev-api.impb.in/v1/document" \
-Method "POST" \
-WebSession $session \
-Headers @{
"method"="POST"
  "authority"="dev-api.impb.in"
  "scheme"="https"
  "path"="/v1/document"
  "sec-ch-ua"="\"Chromium\";v=\"94\", \" Not A;Brand\";v=\"99\", \"Opera GX\";v=\"80\""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="\"Windows\""
  "accept"="*/*"
  "origin"="https://dev.impb.in"
  "sec-fetch-site"="same-site"
  "sec-fetch-mode"="cors"
  "sec-fetch-dest"="empty"
  "referer"="https://dev.impb.in/"
  "accept-encoding"="gzip, deflate, br"
  "accept-language"="en-US,en;q=0.9"
} \
-ContentType "application/json" \
-Body "{\"content\":\"yeah\",\"settings\":{\"longUrls\":false,\"shortUrls\":false,\"instantDelete\":false,\"encrypted\":false,\"imageEmbed\":false,\"expiration\":14,\"public\":false,\"editors\":[],\"language\":\"python\"}}"'''

powershell_samples[powershell_example_two] = Method(
    method="POST",
    url=URL("https://dev-api.impb.in/v1/document"),
    body=Body(
        '{"content":"yeah","settings":{"longUrls":false,"shortUrls":false,"instantDelete":false,"encrypted":false,"imageEmbed":false,"expiration":14,"public":false,"editors":[],"language":"python"}}'
    ),
    parameters=None,
    cookies={},
    headers={
        "authority": "dev-api.impb.in",
        "scheme": "https",
        "path": "/v1/document",
        "sec-ch-ua": '"Chromium";v="94", " Not A;Brand";v="99", "Opera GX";v="80"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "accept": "*/*",
        "origin": "https://dev.impb.in",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://dev.impb.in/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 OPR/80.0.4170.48",
    },
)
