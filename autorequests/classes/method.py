from . import URL, Body, Parameter
from ..utils import format_dict, indent


class Method:
    # set for performance
    __accepted_chars = {"_", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S",
                        "T", "U", "V", "W", "X", "Y", "Z",
                        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
                        "t", "u", "v", "w", "x", "y", "z"}

    def __init__(self,
                 method: str,
                 url: URL,
                 body: Body,
                 parameters: list[Parameter] = None,
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

        # remove leading and trailing / for calculation
        path = self.url.path
        split = [i for i in path.split("/") if i][::-1]

        # find parts of path that meets python's syntax requirements for a method name

        for sector in split:
            # -s and .s are not actually allowed, they will be replaced with _s
            sector = sector.replace("-", "_")
            sector = sector.replace(".", "_")
            if not sector or sector[0].isdigit():
                continue
            # for larger operators, it could be faster to do .lower() and then skip checking uppercase characters
            # this doesn't have a big performance increase though, and it's actually slower with smaller strings
            if all(char in self.__accepted_chars for char in sector):
                self.__name = sector
                break
        else:
            if len(split) == 0:
                self.__name = self.class_name
            else:
                # this will have an error in the generated code
                self.__name = split[-1]

    def __repr__(self):
        return f"<{self.signature}>"

    @property
    def signature(self):
        return f"def {self.name}({', '.join(param.code() for param in self.parameters)}):"

    def code(self,
             banned_headers: dict = None,
             banned_cookies: dict = None):
        # handle class headers & cookies
        banned_headers = banned_headers or {}
        banned_cookies = banned_cookies or {}
        headers = {header: value for header, value in self.headers.items() if header not in banned_headers}
        cookies = {cookie: value for cookie, value in self.cookies.items() if cookie not in banned_cookies}
        # code
        body = f"return self.session.{self.method.lower()}(\"{self.url}\""
        for kwarg, data in {"params": self.url.query,
                            "data": self.body.data,
                            "json": self.body.json,
                            "files": self.body.files,
                            "headers": headers,
                            "cookies": cookies}.items():
            if data:
                body += f", {kwarg}=" + format_dict(data)
        body += ").json()"
        return self.signature + "\n" + indent(body, spaces=4)

    @property
    def parameters(self) -> list[Parameter]:
        return self.__parameters

    def add_parameter(self, param: Parameter):
        self.__parameters.append(param)

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
    def headers(self):
        return self.__headers

    @headers.setter
    def headers(self, new_headers: dict[str]):
        if isinstance(new_headers, dict):
            self.__headers = new_headers

    @property
    def cookies(self):
        return self.__cookies

    @cookies.setter
    def cookies(self, new_cookies: dict[str]):
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
