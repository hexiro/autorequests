from typing import List, Dict

from . import URL, Body, Parameter, Case
from ..utils import format_dict, indent, is_valid_function_name


class Method:

    def __init__(self,
                 method: str,
                 url: URL,
                 body: Body,
                 parameters: List[Parameter] = None,
                 headers: Dict[str] = None,
                 cookies: Dict[str] = None,
                 ):
        self.__method = method
        self.__url = url
        # request body -- not to be confused with method body
        self.__body = body
        self.__headers = headers or {}
        self.__cookies = cookies or {}
        # params
        self.__parameters = [Parameter("self")]
        for param in (parameters or []):
            if param.name != "self":
                self.__parameters.append(param)

        self.__name = self.default_name
        self.__class = None

    def __repr__(self):
        return f"<{self.signature}>"

    def attach_class(self, class_):
        """
        :type class_: Class
        """
        self.__class = class_

    @property
    def class_(self):
        """
        :rtype: Class
        """
        return self.__class

    @property
    def class_headers(self):
        return getattr(self.class_, "headers", {})

    @property
    def class_cookies(self):
        return getattr(self.class_, "cookies", {})

    @property
    def return_text(self):
        return getattr(self.class_, "return_text", False)

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
                body += f", {kwarg}=" + format_dict(data)
        body += ")."
        body += "text" if self.return_text else "json()"
        return self.signature + "\n" + indent(body, spaces=4)

    @property
    def parameters(self) -> List[Parameter]:
        return self.__parameters

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
