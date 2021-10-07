import json
from pathlib import Path
from typing import Optional, List, Generator

from . import URL, Body, Method, Class
from .. import regexp
from ..utils import extract_cookies, cached_property


class Input:
    """ handles files and the parsing of files """

    def __init__(self, input_path: Path, output_path: Path):
        self.__input_path: Path = input_path
        self.__output_path: Path = output_path
        self.__input_files: List[Path] = []
        self.__methods: List[Method] = self.methods_from_path(self.input_path)
        self.__classes: List[Class] = [Class(name=name) for name in {method.class_name for method in self.methods}]

        for cls in self.classes:
            folder = self.class_output_path(cls)
            self.methods.extend(self.methods_from_path(folder))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} methods={self.methods}>"

    @property
    def input_path(self) -> Path:
        return self.__input_path

    @property
    def output_path(self) -> Path:
        return self.__output_path

    @property
    def input_files(self):
        return self.__input_files

    @cached_property
    def methods(self) -> List[Method]:
        return self.__methods

    @cached_property
    def classes(self) -> List[Class]:
        return self.__classes

    def class_output_path(self, cls: Class):
        if self.output_path.name != cls.name:
            return self.output_path / cls.name
        # ex. class is named "autorequests" and output folder is named "autorequests"
        return cls

    def methods_from_path(self, path: Path) -> List[Method]:
        methods = []
        for file in self.files_from_path(path):
            text = file.read_text(encoding="utf8", errors="ignore")
            method = self.method(text)
            if method is None:
                continue
            methods.append(method)
            self.input_files.append(file)
        return methods

    @staticmethod
    def files_from_path(path: Path) -> Generator[Path, None, None]:
        return path.glob("*.txt")

    def find_class(self, name: str) -> Optional[Class]:
        return next((cls for cls in self.classes if cls.name == name), None)

    @classmethod
    def method(cls, text: str) -> Optional[Method]:
        # short circuiting
        if text:
            return cls.method_from_fetch(text) or cls.method_from_powershell(text)

    @staticmethod
    def method_from_fetch(text: str) -> Optional[Method]:
        """
        Parses a file that follows this format:
        (with some being optional)

        fetch(<URL>, {
          "headers": <HEADERS>,
          "referrer": <REFERRER>,
          "referrerPolicy": <REFERRER-POLICY>,
          "body": <BODY>,
          "method": <METHOD>,
          "mode": <MODE>
        });
        """
        fetch = regexp.fetch_regexp.search(text)
        if not fetch:
            return

        headers = json.loads(fetch["headers"])
        # referer is spelled wrong in the HTTP header
        # referrer policy is not
        referrer = fetch["referrer"]
        referrer_policy = fetch["referrer_policy"]
        if referrer:
            headers["referer"] = referrer
        if referrer_policy:
            headers["referrer-policy"] = referrer_policy

        cookies = extract_cookies(headers)

        method = fetch["method"]
        url = URL(fetch["url"])
        body = Body(fetch["body"])

        return Method(method=method,
                      url=url,
                      body=body,
                      headers=headers,
                      cookies=cookies,
                      )

    @staticmethod
    def method_from_powershell(text: str) -> Optional[Method]:
        """
        Parses a file that follows this format:
        (with some potentially being optional)

        Invoke-WebRequest -Uri <URL> `
        -Method <METHOD> `   # optional; defaults to GET if not set
        -Headers <HEADERS> `
        -ContentType <CONTENT-TYPE> `   # optional; only exists w/ body
        -Body <BODY>     # optional; only exists if a body is present
        """
        powershell = regexp.powershell_regexp.search(text)
        if not powershell:
            return

        headers = {}
        for header in powershell["headers"].splitlines():
            if "=" in header:
                header = header.lstrip("  ")
                key, value = header.split("=", maxsplit=1)
                # remove leading and trailing "s that always exist
                key = key[1:-1]
                value = value[1:-1]
                headers[key] = value

        cookies = extract_cookies(headers)

        # ` is the escape character in powershell
        # replace two `s with a singular `
        # replace singular `s with nothing

        raw_body = powershell["body"]
        if raw_body:
            raw_body = raw_body.split("`")
            raw_body = "".join((e if e != "" else "`") for e in raw_body)

        method = powershell["method"] or "GET"
        url = URL(powershell["url"])
        body = Body(raw_body)

        return Method(method=method,
                      url=url,
                      body=body,
                      headers=headers,
                      cookies=cookies,
                      )
