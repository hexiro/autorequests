from autorequests.parsing.powershell import parse_powershell_to_method

powershell_example = """$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
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


def test_parse_powershell_to_method():
    method = parse_powershell_to_method(powershell_example)
    assert method.cookies == {"hello-from": "autorequests"}
    assert method.headers == {
        "authority": "httpbin.org",
        "scheme": "https",
        "path": "/cookies",
        "sec-ch-ua": "\"Chromium\";v=\"94\", \" Not A;Brand\";v=\"99\", \"Opera GX\";v=\"80\"",
        "accept": "application/json",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://httpbin.org/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/94.0.4606.61 Safari/537.36 OPR/80.0.4170.48 "
    }
