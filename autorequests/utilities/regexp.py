import re

powershell_regexp = re.compile(
    r"^Invoke-WebRequest -Uri \""
    r"(?P<url>(?:http|https):\/\/.+?)\"(?: `\n-Method \""
    r"(?P<method>[A-Z]+)\"|)(?:(?: | `\n)-Headers @{(?:\n\"method\"=\"[A-Z]+\"|)\n"
    r"(?P<headers>(?:(?:  |)\".+?\"=\".+?\"\n)*)}|)(?: `\n-ContentType \""
    r"(?P<content_type>.+)\"|)(?: `\n-Body \""
    r"(?P<body>.+)\"|)$"
)

fix_snake_case_regexp = re.compile("_{2,}")
leading_integer_regexp = re.compile("^[0-9]+")