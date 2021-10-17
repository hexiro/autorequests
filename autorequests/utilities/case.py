import string

from . import uses_accepted_chars
from .regexp import fix_snake_case_regexp

# accepted chars for each case convention
SNAKE_CASE_CHARS = string.ascii_lowercase + "_"
KEBAB_CASE_CHARS = string.ascii_lowercase + "-"
DOT_CASE_CHARS = string.ascii_lowercase + "."
CAMEL_CASE_CHARS = string.ascii_letters
PASCAL_CASE_CHARS = string.ascii_letters


def snake_case(text: str):
    """
    Tries to parse snake case from an unknown case convention
    """
    if is_no_case(text):
        return text
    if is_kebab_case(text):
        return kebab_to_snake(text)
    if is_dot_case(text):
        return dot_to_snake(text)
    if is_camel_case(text):
        return camel_to_snake(text)
    if is_pascal_case(text):
        return pascal_to_snake(text)
    # attempt to parse text
    snaked_text = text
    snaked_text = kebab_to_snake(snaked_text)
    snaked_text = dot_to_snake(snaked_text)
    snaked_text = camel_to_snake(snaked_text)
    # pascal to snake and camel to snake are the same function, so pascal isn't needed
    return fix_snake_case_regexp.sub("_", snaked_text)


def camel_case(text: str):
    return snake_to_camel(snake_case(text))


def pascal_case(text: str):
    return snake_to_pascal(snake_case(text))


def kebab_case(text: str):
    return snake_to_kebab(snake_case(text))


def dot_case(text: str):
    return snake_to_dot(snake_case(text))


def is_no_case(text: str) -> bool:
    """
    :returns: true if text is a single lowercase word
    that could be considered any case convention really (besides pascal ig)
    """
    return text.islower() and uses_accepted_chars(text, string.ascii_lowercase)


def is_snake_case(text: str) -> bool:
    return text.islower() and uses_accepted_chars(text, SNAKE_CASE_CHARS)


def is_kebab_case(text: str) -> bool:
    return text.islower() and uses_accepted_chars(text, KEBAB_CASE_CHARS)


def is_dot_case(text: str) -> bool:
    return text.islower() and uses_accepted_chars(text, DOT_CASE_CHARS)


def is_camel_case(text: str) -> bool:
    return text[0].islower() and not text.islower() and \
           uses_accepted_chars(text, CAMEL_CASE_CHARS)


def is_pascal_case(text: str) -> bool:
    return text[0].isupper() and uses_accepted_chars(text, PASCAL_CASE_CHARS)


def camel_to_snake(text: str) -> str:
    return "".join("_" + t.lower() if t.isupper() else t for t in text).lstrip("_")


pascal_to_snake = camel_to_snake


def kebab_to_snake(text: str) -> str:
    return text.replace("-", "_")


def dot_to_snake(text: str) -> str:
    return text.replace(".", "_")


def snake_to_camel(text: str) -> str:
    return "".join(t.lower() if i == 0 else t.capitalize() for i, t in enumerate(text.split("_")))


def snake_to_pascal(text: str) -> str:
    return "".join(t.capitalize() for t in text.split("_"))


def snake_to_kebab(text: str) -> str:
    return text.replace("_", "-").lower()


def snake_to_dot(text: str) -> str:
    return text.replace("_", ".").lower()
