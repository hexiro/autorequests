from pathlib import Path
from typing import TYPE_CHECKING, List, Dict

from ..utilities import format_dict, indent, merge_dicts, cached_property

if TYPE_CHECKING:
    from .method import Method


# "class" is a reserved keyword so I can't name a file "class"


class Class:
    def __init__(
        self,
        name: str,
        output_path: Path,
        return_text: bool = False,
        no_headers: bool = False,
        no_cookies: bool = False,
        parameters: bool = False,
    ):
        self._name: str = name
        self._output_path: Path = output_path
        self._methods: List["Method"] = []
        self._cookies: Dict[str, str] = {}
        self._headers: Dict[str, str] = {}

        self._return_text: bool = return_text
        self._no_headers: bool = no_headers
        self._no_cookies: bool = no_cookies
        self._parameters: bool = parameters

    def __repr__(self) -> str:
        return f"<Class {self.name}>"

    @property
    def name(self) -> str:
        return self._name

    @property
    def output_path(self) -> Path:
        return self._output_path

    @property
    def methods(self) -> List["Method"]:
        return self._methods

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @property
    def cookies(self) -> Dict[str, str]:
        return self._cookies

    @property
    def return_text(self) -> bool:
        return self._return_text

    @property
    def parameters(self) -> bool:
        return self._parameters

    @property
    def no_headers(self) -> bool:
        return self._no_headers

    @property
    def no_cookies(self) -> bool:
        return self._no_cookies

    @cached_property
    def folder(self) -> Path:
        if self.output_path.name != self.name:
            return self.output_path / self.name
        # ex. class is named "autorequests" and output folder is named "autorequests"
        return self.output_path

    @property
    def file(self) -> Path:
        return self.folder / "main.py"

    @property
    def signature(self) -> str:
        return f"class {self.name}:"

    @property
    def initializer(self) -> str:
        signature = "def __init__(self):\n"
        code = "self.session = requests.Session()\n"
        if self.headers:
            code += "self.session.headers.update("
            code += format_dict(self.headers)
            code += ")\n"
        for cookie, value in self.cookies.items():
            code += f'self.session.cookies.set("{cookie}", "{value}")\n'
        return signature + indent(code)

    @property
    def use_initializer(self) -> bool:
        return bool(self.headers or self.cookies)

    @property
    def code(self) -> str:
        # not actually two newlines; adds \n to end of previous line
        code = self.signature + "\n\n"
        if self.use_initializer:
            code += indent(self.initializer)
        for method in self.methods:
            code += indent(method.code)
        return code + "\n"

    def add_method(self, method: "Method") -> None:
        method.class_ = self
        method.ensure_unique_name()
        self._methods.append(method)
        if len(self.methods) >= 2:
            self._headers = merge_dicts(*(method.local_headers for method in self.methods))
            self._cookies = merge_dicts(*(method.local_cookies for method in self.methods))

        if self.no_headers:
            method.remove_headers()
        if self.no_cookies:
            method.remove_cookies()
