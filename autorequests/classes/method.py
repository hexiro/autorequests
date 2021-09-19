from typing import List, Dict

from . import URL, Body, Parameter, Case
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
        self.__method = method
        self.__url = url
        # request body -- not to be confused with method body
        self.__body = body
        # must append to `parameters` property, and not __parameters
        self.__parameters = parameters
        self.__headers = headers or {}
        self.__cookies = cookies or {}
        self.__name = self.default_name
        self.__class = None

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

    @cached_property
    def parameters(self) -> List[Parameter]:
        params = self.__parameters or []
        if params[0].name != "self":
            params.insert(0, Parameter("self"))
        if self.class_.parameters_mode:
            for key, value in {**self.url.query,
                               **self.body.data,
                               **self.body.json,
                               **self.body.files}.items():
                params.append(Parameter(key, default=value))
        return params

    @property
    def signature(self):
        return f"def {self.name}({', '.join(param.code for param in self.parameters)}):"

    @cached_property
    def code(self):
        # handle class headers & cookies
        # only use session if headers or cookies are set in class
        requests_call = "self.session" if (self.class_.use_constructor) else "requests"
        # code
        body = f"return {requests_call}.{self.method.lower()}(\"{self.url}\""
        for kwarg, data in {"params": self.url.query,
                            "data": self.body.data,
                            "json": self.body.json,
                            "files": self.body.files,
                            "headers": self.headers,
                            "cookies": self.cookies}.items():
            if data:
                if self.class_.parameters_mode:
                    parameters_dict = {p.name: p for p in self.parameters}
                    for key, value in data.items():
                        data[key] = parameters_dict[key].name if key in parameters_dict else value
                    formatted_data = format_dict(data, variables=[p.name for p in self.parameters])
                else:
                    formatted_data = format_dict(data)
                body += f", {kwarg}=" + formatted_data
        body += ")."
        body += "text" if self.class_.return_text else "json()"
        return self.signature + "\n" + indent(body, spaces=4)

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
        if self.class_headers:
            return {h: v for h, v in self.__headers.items() if h not in self.class_.headers}
        return self.__headers

    @headers.setter
    def headers(self, new_headers: Dict[str, str]):
        if isinstance(new_headers, dict):
            self.__headers = new_headers

    @property
    def cookies(self):
        if self.class_cookies:
            return {c: v for c, v in self.__headers.items() if c not in self.class_.cookies}
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
