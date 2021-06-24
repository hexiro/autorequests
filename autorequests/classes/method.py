from typing import List, Dict

from . import URL, Body, Parameter, Case
from ..utils import format_dict, indent, is_valid_function_name


class Method:

    def __init__(self,
                 method: str,
                 url: URL,
                 body: Body,
                 parameters: List[Parameter] = None,
                 headers: dict = None,
                 cookies: dict = None,
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
            self.__parameters.append(param)

        self.__name = self.default_method_name

    def __repr__(self):
        return f"<{self.signature}>"

    @property
    def signature(self):
        return f"def {self.name}({', '.join(param.code() for param in self.parameters)}):"

    def code(self,
             class_headers: dict = None,
             class_cookies: dict = None,
             return_text: bool = False):
        # handle class headers & cookies
        class_headers = class_headers or {}
        class_cookies = class_cookies or {}
        # only use session if headers or cookies are set in class
        if class_headers or class_cookies:
            headers = {header: value for header, value in self.headers.items() if header not in class_headers}
            cookies = {cookie: value for cookie, value in self.cookies.items() if cookie not in class_cookies}
            requests_call = "self.session"
        else:
            headers = self.headers
            cookies = self.cookies
            requests_call = "requests"
        # code
        body = f"return {requests_call}.{self.method.lower()}(\"{self.url}\""
        for kwarg, data in {"params": self.url.query,
                            "data": self.body.data,
                            "json": self.body.json,
                            "files": self.body.files,
                            "headers": headers,
                            "cookies": cookies}.items():
            if data:
                body += f", {kwarg}=" + format_dict(data)
        body += ")."
        body += "text" if return_text else "json()"
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
    def default_method_name(self):
        # remove leading and trailing / for calculation
        split = self.url.path.split("/")[::-1]
        # find parts of path that meets python's syntax requirements for a method name
        for sector in split:
            sector = Case(sector).snake_case
            if is_valid_function_name(sector):
                return sector
        # using base domain -- same name as class
        if len(split) == 0:
            return self.class_name
        # this will have an error in the generated code
        return split[-1]

    @property
    def headers(self):
        return self.__headers

    @headers.setter
    def headers(self, new_headers: Dict[str, str]):
        if isinstance(new_headers, dict):
            self.__headers = new_headers

    @property
    def cookies(self):
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
