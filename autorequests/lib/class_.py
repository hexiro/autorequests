from pathlib import Path
from typing import List, Dict

from . import method
from ..utilities import format_dict, indent, compare_dicts, cached_property


# "class" is a reserved keyword so I can't name a file "class"

class Class:

    def __init__(self,
                 name: str,
                 output_path: Path,
                 return_text: bool = False,
                 no_headers: bool = False,
                 no_cookies: bool = False,
                 parameters: bool = False):
        self._name: str = name
        self._output_path: Path = output_path
        self._methods: List["method.Method"] = []
        self._cookies: Dict[str, str] = {}
        self._headers: Dict[str, str] = {}

        self._return_text: bool = return_text
        self._no_headers: bool = no_headers
        self._no_cookies: bool = no_cookies
        self._parameters: bool = parameters

    def __repr__(self):
        return f"<Class {self.name}>"

    @property
    def name(self):
        return self._name

    @property
    def output_path(self):
        return self._output_path

    @property
    def methods(self):
        return self._methods

    @property
    def headers(self):
        return self._headers

    @property
    def cookies(self):
        return self._cookies

    @property
    def return_text(self):
        return self._return_text

    @property
    def parameters(self):
        return self._parameters

    @property
    def no_headers(self):
        return self._no_headers

    @property
    def no_cookies(self):
        return self._no_cookies

    @cached_property
    def folder(self) -> Path:
        if self.output_path.name != self.name:
            return self.output_path / self.name
        # ex. class is named "autorequests" and output folder is named "autorequests"
        return self.output_path

    @property
    def file(self):
        return self.folder / "main.py"

    @property
    def signature(self):
        return f"class {self.name}:"

    @property
    def initializer(self):
        signature = "def __init__(self):\n"
        code = "self.session = requests.Session()\n"
        if self.headers:
            code += "self.session.headers.update("
            code += format_dict(self.headers)
            code += ")\n"
        for cookie, value in self.cookies.items():
            code += f"self.session.cookies.set(\"{cookie}\", \"{value}\")\n"
        return signature + indent(code)

    @property
    def use_initializer(self) -> bool:
        return bool(self.headers or self.cookies)

    @property
    def code(self):
        code = self.signature
        # not actually two newlines; adds \n to end of previous line
        if self.use_initializer:
            code += "\n\n"
            code += indent(self.initializer)
        for method in self.methods:
            code += "\n\n"
            code += indent(method.code)
        code += "\n"
        return code

    def add_method(self, method: "method.Method"):
        method.class_ = self
        method.ensure_unique_name()
        self._methods.append(method)
        if len(self.methods) >= 2:
            self._headers = compare_dicts(*(method.all_headers for method in self.methods))
            self._cookies = compare_dicts(*(method.all_cookies for method in self.methods))

        if self.no_headers:
            method.remove_headers()
        if self.no_cookies:
            method.remove_cookies()
