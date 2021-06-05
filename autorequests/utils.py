import json


# pretty simplistic names tbf
# a lot of these aren't super self explanatory so they have docstring

def indent(data: str, spaces: int = 4) -> str:
    """ add spaces by newline """
    return "\n".join(" " * spaces + line for line in data.splitlines())


# i'm hoping this is more useful when i add more options besides fetch

def cookies(headers: dict[str]):
    """ :returns: a dict of cookies based off the 'cookie' header """
    cookie_header = headers.pop("cookie", None)
    if not cookie_header:
        return {}
    cookie_dict = {}
    for cookie in cookie_header.split("; "):
        key, value = cookie.split("=", maxsplit=1)
        cookie_dict[key] = value
    return cookie_dict


def compare_dicts(dicts: list[dict]) -> dict:
    """ :returns: a dictionary with the items that all of the dicts in the list share """
    # if there is 0 or 1 dicts, there will be no matches
    if len(dicts) <= 1:
        return {}

    # they ALL have to share an item for it to be accepted,
    # therefore we can just loop over the first dict in the list and check if it matches the other items
    return {k: v for k, v in dicts[0].items() if all(dict_.get(k) == v for dict_ in dicts[1:])}


# compare_lists isn't used yet

def compare_lists(lists: list[list]) -> list:
    """ :returns: a list of items that all the lists share """
    # if there is 0 or 1 lists, there will be no matches
    if len(lists) <= 1:
        return []

    # they ALL have to contain an item for it to be accepted,
    # therefore we can just loop over the first list in the list and check all the other lists share the match
    return [p for i, p in enumerate(lists[0]) if all(list_[i] == p for list_ in lists[1:])]


def format_dict(data: dict) -> str:
    """ format a dictionary """

    # I'm not sure it's possible to pretty-format this with something like
    # pprint, but if it is possible LMK!

    formatted = json.dumps(data, indent=4)
    # parse bools and none
    # I believe this is all I need to replace
    # leading space allows us to only match literal false and not "false" string
    formatted = formatted.replace(" null", " None")
    formatted = formatted.replace(" true", " True")
    formatted = formatted.replace(" false", " False")
    return formatted


# kinda fucked if english changes
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


def written_form(num: int) -> str:
    """ :returns: written form of an integer 0-999 """
    if num > 999:
        raise NotImplementedError("numbers > 999 not supported")
    if num == 0:
        return "zero"
    hundreds, tens, ones = str(num).zfill(3)
    ones_match = ones_dict.get(ones)
    tens_match = tens_dict.get(tens)
    unique_match = unique_dict.get((tens + ones))
    hundreds_match = ones_dict.get(hundreds)
    written = []
    if hundreds_match:
        written.append(hundreds_match + " hundred")
    if unique_match:
        written.append(unique_match)
    elif tens_match and ones_match:
        written.append(tens_match + "-" + ones_match)
    elif tens_match:
        written.append(tens_match)
    elif ones_match:
        written.append(ones_match)
    return " and ".join(written)


def unique_name(name: str, other_names: list[str]) -> str:
    """ :returns a unique name based on the name passed and the taken names """
    matches = [item for item in other_names if item.startswith(name)]
    if not any(matches):
        return name
    matched_names_length = len(matches)
    if matched_names_length > 999:
        raise NotImplementedError(">999 methods with similar names not supported")
    written = written_form(matched_names_length + 1).replace(" ", "_").replace("-", "_")
    return name + "_" + written


def combine_dicts(dicts: list[dict]) -> dict:
    """ combines dicts with unique names """
    combined = {}
    for dict_ in dicts:
        for key, value in dict_.items():
            if key in combined:
                key = unique_name(name=key,
                                  other_names=list(combined.keys()))
            combined[key] = value
    return combined
