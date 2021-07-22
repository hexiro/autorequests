from typing import List, Dict

from . import URL, Body, Parameter, Case
from ..utils import format_dict, indent, is_valid_function_name, cached_property


class Method:

    def __init__(self,
                 method: str,
                 url: URL,
                 body: Body,
                 parameters: List[Parameter] = None,
                 headers: Dict[str, str] = None,
                 cookies: Dict[str, str] = None
                 ):
        self.__method = method
        self.__url = url
        # request body -- not to be confused with method body
        self.__body = body
        self.__parameters = parameters
        self.__headers = headers or {}
        self.__cookies = cookies or {}
        self.__name = self.default_name
        self.__class = None
        # params

    def __repr__(self):
        return f"<{self.signature}>"

    @property
    def class_(self):
        """
        :rtype: Class
        """
        return self.__class

    @class_.setter
    def class_(self, new_class):
        """
        :type new_class: Class
        """
        self.__class = new_class

    @property
    def class_headers(self) -> Dict[str, str]:
        return getattr(self.class_, "headers", {})

    @property
    def class_cookies(self) -> Dict[str, str]:
        return getattr(self.class_, "cookies", {})

    @property
    def return_text(self) -> bool:
        return getattr(self.class_, "return_text", False)

    @property
    def parameters_mode(self) -> bool:
        return getattr(self.class_, "parameters_mode", False)

    @cached_property
    def parameters(self) -> List[Parameter]:
        params = [Parameter("self")]
        for param in (self.__parameters or []):
            if param.name != "self":
                params.append(param)
        if self.parameters_mode:
            data = {**self.url.query, **self.body.data, **self.body.json, **self.body.files}
            for index, (key, value) in enumerate(data.items()):
                params.append(Parameter(key, default=value))
        return params

    @property
    def signature(self):
        return f"def {self.name}({', '.join(param.code for param in self.parameters)}):"

    @property
    def code(self):
        # handle class headers & cookies
        # only use session if headers or cookies are set in class
        requests_call = "self.session" if (self.class_headers or self.class_cookies) else "requests"
        # code
        body = f"return {requests_call}.{self.method.lower()}(\"{self.url}\""
        for kwarg, data in {"params": self.url.query,
                            "data": self.body.data,
                            "json": self.body.json,
                            "files": self.body.files,
                            "headers": self.headers,
                            "cookies": self.cookies}.items():
            if data:
                if self.parameters_mode:
                    parameters_dict = {p.name: p for p in self.parameters}
                    for key, value in data.items():
                        data[key] = parameters_dict[key].name if key in parameters_dict else value
                body += f", {kwarg}=" + format_dict(data, variables=[p.name for p in self.parameters])
        body += ")."
        body += "text" if self.return_text else "json()"
        return self.signature + "\n" + indent(body, spaces=4)

    @property
    def class_name(self):
        # DOMAIN of url
        # domains with two dots break this (ex. .co.uk)
        class_name = self.url.domain.split(".")[-2]
        # remove port
        class_name = class_name.split(":")[0]
        # replace -s with _s
        class_name = class_name.replace("-", "_")
        return class_name

    @property
    def default_name(self):
        # remove leading and trailing / for calculation
        split = [Case(p).snake_case for p in self.url.path.split("/") if p]
        split.reverse()
        # find parts of path that meets python's syntax requirements for a method name
        for part in split:
            if is_valid_function_name(part):
                return part
        # using base domain -- same name as class
        if not split:
            return self.class_name
        # this will have an error in the generated code
        return split[-1]

    @property
    def headers(self):
        if self.class_headers:
            return {h: v for h, v in self.__headers.items() if h not in self.class_headers}
        return self.__headers

    @headers.setter
    def headers(self, new_headers: Dict[str, str]):
        if isinstance(new_headers, dict):
            self.__headers = new_headers

    @property
    def cookies(self):
        if self.class_cookies:
            return {c: v for c, v in self.__headers.items() if c not in self.class_cookies}
        return self.__cookies

    @cookies.setter
    def cookies(self, new_cookies: Dict[str, str]):
        if isinstance(new_cookies, dict):
            self.__cookies = new_cookies

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_name):
        self.__name = new_name

    @property
    def method(self):
        return self.__method

    @property
    def url(self):
        return self.__url

    @property
    def body(self):
        return self.__body
