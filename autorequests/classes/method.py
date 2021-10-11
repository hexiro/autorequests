from typing import List, Dict, Optional

from . import URL, Body, Parameter
from . import class_
from ..utilities import format_dict, indent, is_pythonic_name, cached_property, unique_name, written_form
from ..utilities.case import camel_case, snake_case


class Method:

    def __init__(self,
                 method: str,
                 url: URL,
                 body: Body,
                 parameters: List[Parameter] = None,
                 headers: Dict[str, str] = None,
                 cookies: Dict[str, str] = None
                 ):
        # request method (ex. GET, POST)
        self._method: str = method
        self._url: URL = url
        # request body -- not to be confused with method body
        self._body: Body = body
        # must append to `parameters` property, and not __parameters
        self._parameters: List[Parameter] = parameters or []
        self._headers: Dict[str, str] = headers or {}
        self._cookies: Dict[str, str] = cookies or {}
        self._name: str = self.default_name
        self._class: Optional["class_.Class"] = None

    def __repr__(self) -> str:
        return f"<{self.signature}>"

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str):
        self._name = new_name

    @property
    def method(self) -> str:
        return self._method

    @property
    def url(self) -> URL:
        return self._url

    @property
    def body(self) -> Body:
        return self._body

    @property
    def signature(self) -> str:
        return f"def {self.name}({', '.join(param.code for param in self.parameters)}):"

    @property
    def class_(self) -> Optional["class_.Class"]:
        return self._class

    @class_.setter
    def class_(self, new_class: "class_.Class"):
        self._class = new_class

    @cached_property
    def parameters(self) -> List[Parameter]:
        params = self._parameters
        if not params or params[0].name != "self":
            params.insert(0, Parameter("self"))
        if self.class_ and self.class_.parameters:
            for key, value in {**self.url.query,
                               **self.body.data,
                               **self.body.json,
                               **self.body.files}.items():
                params.append(Parameter(key, default=value))
        return params

    @cached_property
    def code(self) -> str:
        # only use session if headers or cookies are set in class
        requests_call = "self.session" if self.class_ and self.class_.use_initializer else "requests"
        body = f"{self.docstring}\nreturn {requests_call}.{self.method.lower()}(\"{self.url}\""
        for kwarg, data in {"params": self.url.query,
                            "data": self.body.data,
                            "json": self.body.json,
                            "files": self.body.files,
                            "headers": self.headers,
                            "cookies": self.cookies}.items():
            if not data:
                continue
            variables = None
            if self.class_ and self.class_.parameters:
                variables = [p.name for p in self.parameters]
                for key, value in data.items():
                    data[key] = key if key in variables else value
            body += f", {kwarg}=" + format_dict(data, variables=variables)
        body += ")."
        body += "text" if self.class_ and self.class_.return_text else "json()"
        return self.signature + "\n" + indent(body)

    @property
    def docstring(self) -> str:
        details: List[str] = []
        for kwarg, data in {"param": self.url.query,
                            "data item": self.body.data,
                            "json item": self.body.json,
                            "file": self.body.files,
                            "header": self.headers,
                            "cookie": self.cookies}.items():
            if not data:
                continue
            len_data = len(data)
            # make plural
            if len_data > 1:
                kwarg += "s"
            details.append(f"{len_data} {kwarg}")
        details[-1] = f"and {details[-1]}."
        details_string = ", ".join(details)
        return ("\"\"\"\n"
                f"{self.method} {self.url}.\n"
                f"Contains {details_string}\n"
                "\"\"\"")

    @cached_property
    def class_name(self) -> str:
        # DOMAIN of url
        # domains with two dots break this (ex. .co.uk)
        class_name = self.url.domain.split(".")[-2]
        # remove port
        class_name = class_name.split(":")[0]
        if not class_name[0].isdigit():
            return camel_case(class_name)
        # if class name starts with integer
        initial_num = class_name[0]
        for i in range(1, len(class_name)):
            segment = class_name[:i]
            if segment.isdigit():
                initial_num = segment
            else:
                break
        rest = class_name[len(initial_num):]
        return camel_case(f"{written_form(int(initial_num))}_{rest}")

    @cached_property
    def default_name(self) -> str:
        # remove leading and trailing / for calculation
        split = [snake_case(p) for p in self.url.path.split("/") if p]
        split.reverse()
        # find parts of path that meets python's syntax requirements for a method name
        for part in split:
            if is_pythonic_name(part):
                return part
        # using base domain -- same name as class
        if not split:
            return snake_case(self.class_name)
        # this will have an error in the generated code
        return snake_case(split[-1])

    @property
    def all_headers(self) -> Dict[str, str]:
        return self._headers

    @property
    def headers(self) -> Dict[str, str]:
        if not self._class:
            return self._headers
        return {h: v for h, v in self._headers.items() if h not in self._class.headers}

    @property
    def all_cookies(self) -> Dict[str, str]:
        return self._cookies

    @property
    def cookies(self) -> Dict[str, str]:
        if not self.class_:
            return self._cookies
        return {c: v for c, v in self._cookies.items() if c not in self.class_.cookies}

    def ensure_unique_name(self):
        if not self._class:
            return
        other_methods = self._class.methods
        if not other_methods:
            return
        if len(other_methods) == 1 and other_methods[0].name == self.name:
            other_methods[0].name = f"{self.name}_one"
            self.name = f"{self.name}_two"
            return
        self.name = unique_name(self.name, [method.name for method in other_methods])
