import functools
import json
import keyword
import urllib.parse
from typing import List, Dict, Optional, Callable, Union

from .regexp import leading_integer_regexp

# pretty simplistic names tbf
# a lot of these aren't super self explanatory so they have docstring

__all__ = (
    "cached_property",
    "indent",
    "is_pythonic_name",
    "extract_cookies",
    "merge_dicts",
    "format_dict",
    "parse_url_encoded",
    "written_form",
    "unique_name",
    "fix_escape_chars",
)

try:
    from functools import cached_property
except ImportError:
    def cached_property(func: Callable):  # type: ignore[no-redef]
        return property(functools.lru_cache()(func))


def indent(data: str, spaces: int = 4) -> str:
    """
    indents a code block a set amount of spaces
    note: is ~1.5x faster than textwrap.indent(data, " " * spaces)
    (from my testing)
    """
    # using this var is slightly slower on small operations,
    # and a lot faster on big operations
    indent_block = " " * spaces
    return "\n".join((indent_block + line if line else line) for line in data.splitlines())


def is_pythonic_name(text: str) -> bool:
    """ :returns: true if the string provided is a valid function name """
    return text.isidentifier() and not keyword.iskeyword(text)


def extract_cookies(headers: Dict[str, str]) -> Dict[str, str]:
    """ :returns: a dict of cookies based off the 'cookie' header """
    cookie_header = headers.pop("cookie", None)
    if not cookie_header:
        return {}
    cookie_dict = {}
    for cookie in cookie_header.split("; "):
        key, value = cookie.split("=", maxsplit=1)
        cookie_dict[key] = value
    return cookie_dict


def merge_dicts(*dicts: Dict[str, str]) -> Dict[str, str]:
    """ :returns: a dictionary with the items that all of the dicts in the list share """
    # if there is 0 or 1 dicts, there will be no matches
    if len(dicts) <= 1:
        return {}

    # they ALL have to share an item for it to be accepted,
    # therefore we can just loop over the first dict in the list and check if it matches the other items
    return {k: v for k, v in dicts[0].items() if all(x.get(k) == v for x in dicts[1:])}


def format_dict(data: dict, indent: Optional[int] = 4, variables: List[str] = None) -> str:
    """ format a dictionary """
    variables = variables or []
    # I'm not sure it's possible to pretty-format this with something like
    # pprint, but if it is possible LMK!
    formatted = json.dumps(data, indent=indent)
    # parse bools and none
    # leading space allows us to only match literal false and not "false" string
    formatted = formatted.replace(" null", " None")
    formatted = formatted.replace(" true", " True")
    formatted = formatted.replace(" false", " False")
    # parse when key names are the same as value
    # leading ": " means that it will replace the value and not the key
    for var in variables:
        formatted = formatted.replace(f": \"{var}\"", f": {var}")
    return formatted


def parse_url_encoded(data: str) -> Dict[str, str]:
    """ parses application/x-www-form-urlencoded and query string params """
    return dict(urllib.parse.parse_qsl(data, keep_blank_values=True))


# kinda screwed if english changes
# if english has progressed please make a pr :pray:

ones_dict = {"1": "one",
             "2": "two",
             "3": "three",
             "4": "four",
             "5": "five",
             "6": "six",
             "7": "seven",
             "8": "eight",
             "9": "nine"}

tens_dict = {"1": "ten",
             "2": "twenty",
             "3": "thirty",
             "4": "forty",
             "5": "fifty",
             "6": "sixty",
             "7": "seventy",
             "8": "eighty",
             "9": "ninety"}

unique_dict = {"11": "eleven",
               "12": "twelve",
               "13": "thirteen",
               "14": "fourteen",
               "15": "fifteen",
               "16": "sixteen",
               "17": "seventeen",
               "18": "eighteen",
               "19": "nineteen"}


def written_form(num: Union[int, str]) -> str:
    """ :returns: written form of an integer 0-999, or for the leading integer of a string """
    if isinstance(num, str):
        # if string is an integer
        if num.isdigit():
            return written_form(int(num))
        # try to parse leading integer
        match = leading_integer_regexp.search(num)
        if not match:
            return num
        # if str starts with integer
        initial_num = match.group(0)
        written_num = written_form(int(initial_num))
        rest = num[match.end():]
        return f"{written_num}_{rest}"
    if num > 999:
        raise NotImplementedError("numbers > 999 not supported")
    if num < 0:
        raise NotImplementedError("numbers < 0 not supported")
    if num == 0:
        return "zero"
    # mypy & pycharm don't like string unpacking
    full_num = str(num).zfill(3)
    hundreds = full_num[0]
    tens = full_num[1]
    ones = full_num[2]
    ones_match = ones_dict.get(ones)
    tens_match = tens_dict.get(tens)
    unique_match = unique_dict.get((tens + ones))
    hundreds_match = ones_dict.get(hundreds)
    written = []
    if hundreds_match:
        written.append(hundreds_match + "_hundred")
    if unique_match:
        written.append(unique_match)
    elif tens_match and ones_match:
        written.append(tens_match + "_" + ones_match)
    elif tens_match:
        written.append(tens_match)
    elif ones_match:
        written.append(ones_match)
    return "_and_".join(written)


def unique_name(name: str, other_names: List[str]) -> str:
    """ :returns a unique name based on the name passed and the taken names """
    matches = [item for item in other_names if item.startswith(name)]
    if not any(matches):
        return name
    matched_names_length = len(matches)
    if matched_names_length > 999:
        raise NotImplementedError(">999 methods with similar names not supported")
    written = written_form(matched_names_length + 1)
    return name + "_" + written


def fix_escape_chars(text: str) -> str:
    """
    replaces escaped \\ followed by a letter to the appropriate char
    ignore/replace are kind of just guesses at what i think would be best
    if there is a more logical reason to use something else LMK!
    (ex. "\\t" --> "\t")
    """
    return (text
            .encode(encoding="utf8", errors="ignore")
            .decode(encoding="unicode_escape", errors="replace"))
