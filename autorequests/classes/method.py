from typing import List, Dict, Optional

from . import URL, Body, Parameter, Case
from . import class_
from ..utils import format_dict, indent, is_pythonic_name, cached_property


class Method:

    def __init__(self,
                 method: str,
                 url: URL,
                 body: Body,
                 parameters: List[Parameter] = None,
                 headers: Dict[str, str] = None,
                 cookies: Dict[str, str] = None
                 ):
        self._method = method
        self._url = url
        # request body -- not to be confused with method body
        self._body = body
        # must append to `parameters` property, and not __parameters
        self._parameters = parameters or []
        self._headers = headers or {}
        self._cookies = cookies or {}
        self._name = self.default_name
        self._class: Optional["class_.Class"] = None

    def __repr__(self):
        return f"<{self.signature}>"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def method(self):
        return self._method

    @property
    def url(self):
        return self._url

    @property
    def body(self):
        return self._body

    @property
    def signature(self):
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
    def code(self):
        # handle class headers & cookies
        # only use session if headers or cookies are set in class
        requests_call = "self.session" if self.class_.use_constructor else "requests"
        # code
        body = f"return {requests_call}.{self.method.lower()}(\"{self.url}\""
        for kwarg, data in {"params": self.url.query,
                            "data": self.body.data,
                            "json": self.body.json,
                            "files": self.body.files,
                            "headers": self.headers,
                            "cookies": self.cookies}.items():
            if not data:
                continue
            variables = None
            if self.class_.parameters:
                variables = [p.name for p in self.parameters]
                for key, value in data.items():
                    data[key] = key if key in variables else value
            body += f", {kwarg}=" + format_dict(data, variables=variables)
        body += ")."
        body += "text" if self.class_.return_text else "json()"
        return self.signature + "\n" + indent(body)

    @cached_property
    def class_name(self):
        # DOMAIN of url
        # domains with two dots break this (ex. .co.uk)
        class_name = self.url.domain.split(".")[-2]
        # remove port
        class_name = class_name.split(":")[0]
        return Case(class_name).camel_case

    @cached_property
    def default_name(self):
        # remove leading and trailing / for calculation
        split = [Case(p).snake_case for p in self.url.path.split("/") if p]
        split.reverse()
        # find parts of path that meets python's syntax requirements for a method name
        for part in split:
            if is_pythonic_name(part):
                return part
        # using base domain -- same name as class
        if not split:
            return self.class_name
        # this will have an error in the generated code
        return split[-1]

    @property
    def headers(self):
        if self.class_.headers:
            return {h: v for h, v in self._headers.items() if h not in self.class_.headers}
        return self._headers

    @headers.setter
    def headers(self, new_headers: Dict[str, str]):
        if isinstance(new_headers, dict):
            self._headers = new_headers

    @property
    def cookies(self):
        if self.class_.cookies:
            return {c: v for c, v in self._headers.items() if c not in self.class_.cookies}
        return self._cookies

    @cookies.setter
    def cookies(self, new_cookies: Dict[str, str]):
        if isinstance(new_cookies, dict):
            self._cookies = new_cookies
