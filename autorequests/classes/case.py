import string

from ..regexp import fix_snake_case_regexp
from ..utils import uses_accepted_chars, cached_property


class Case:
    # accepted chars for each case convention
    snake_case_chars = string.ascii_lowercase + "_"
    kebab_case_chars = string.ascii_lowercase + "-"
    dot_case_chars = string.ascii_lowercase + "."
    camel_case_chars = string.ascii_letters
    pascal_case_chars = string.ascii_letters

    def __init__(self, text: str):
        self.__text = text

    @property
    def text(self):
        return self.__text

    @cached_property
    def snake_case(self):
        if self.is_no_case:
            return self.text
        if self.is_kebab_case:
            return self.kebab_to_snake(self.text)
        if self.is_dot_case:
            return self.dot_to_snake(self.text)
        if self.is_camel_case:
            return self.camel_to_snake(self.text)
        if self.is_pascal_case:
            return self.pascal_to_snake(self.text)
        # attempt to parse text
        snaked_text = self.text
        snaked_text = self.kebab_to_snake(snaked_text)
        snaked_text = self.dot_to_snake(snaked_text)
        snaked_text = self.camel_to_snake(snaked_text)
        # pascal -> snake and camel -> snake are the same function, so pascal isn't needed
        return fix_snake_case_regexp.sub("_", snaked_text)

    @cached_property
    def is_no_case(self) -> bool:
        """
        :returns: true if text is a single lowercase word
        that could be considered any case convention really (besides pascal ig)
        """
        return self.text.islower() and uses_accepted_chars(self.text, string.ascii_lowercase)

    @cached_property
    def is_snake_case(self) -> bool:
        return self.text.islower() and uses_accepted_chars(self.text, self.snake_case_chars)

    @cached_property
    def is_kebab_case(self) -> bool:
        return self.text.islower() and uses_accepted_chars(self.text, self.kebab_case_chars)

    @cached_property
    def is_dot_case(self) -> bool:
        return self.text.islower() and uses_accepted_chars(self.text, self.dot_case_chars)

    @cached_property
    def is_camel_case(self) -> bool:
        return self.text[0].islower() and not self.text.islower() and \
               uses_accepted_chars(self.text, self.camel_case_chars)

    @property
    def is_pascal_case(self) -> bool:
        return self.text[0].isupper() and uses_accepted_chars(self.text, self.pascal_case_chars)

    @staticmethod
    def camel_to_snake(text: str) -> str:
        return "".join("_" + t.lower() if t.isupper() else t for t in text).lstrip("_")

    @classmethod
    def pascal_to_snake(cls, text: str) -> str:
        # pascal and camel case both work here
        return cls.camel_to_snake(text)

    @staticmethod
    def kebab_to_snake(text: str) -> str:
        return text.replace("-", "_")

    @staticmethod
    def dot_to_snake(text: str) -> str:
        return text.replace(".", "_")
