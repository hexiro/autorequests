import re

# https://regex101.com/r/Y6NqA9/15
# ensures general format but not too restrictive with what can be passed
# basically just allows all possible chars for everything as long as it meets expected format
# I keep learning that things can be optional,
# so now everything besides headers is optional just in case
fetch_regexp = re.compile(
    r"^fetch\(\"(?P<url>(?:http|https):\/\/.+)\", {\n  \"headers\": (?P<headers>{(?:.|\n)+}),\n"
    r"(?:  \"referrer\": \"(?P<referrer>.+)\",\n|)"
    r"(?:  \"referrerPolicy\": \"(?P<referrer_policy>.+)\",\n|)"
    r"(?:  \"body\": (?:\"|)(?P<body>.+?)(?:\"|),\n|)"
    r"(?:  \"method\": \"(?P<method>[A-Z]+)\",\n|)"
    r"(?:  \"[a-z]+\": \".+\"(?:,|)\n|)*}\);$"
)

powershell_regexp = re.compile(
    r"^Invoke-WebRequest -Uri \""
    r"(?P<url>(?:http|https):\/\/.+?)\"(?: `\n-Method \""
    r"(?P<method>[A-Z]+)\"|)(?:(?: | `\n)-Headers @{(?:\n\"method\"=\"[A-Z]+\"|)\n"
    r"(?P<headers>(?:(?:  |)\".+?\"=\".+?\"\n)*)}|)(?: `\n-ContentType \""
    r"(?P<content_type>.+)\"|)(?: `\n-Body \""
    r"(?P<body>.+)\"|)$"
)

fix_snake_case_regexp = re.compile("_+")