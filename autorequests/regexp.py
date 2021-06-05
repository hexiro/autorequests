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