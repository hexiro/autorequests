import argparse
import json
import re
from pathlib import Path

from .classes import URL, Body, Method, Class


class FetchHandler(argparse.ArgumentParser):

    # https://regex101.com/r/Y6NqA9/8
    # ensures general format but not too restrictive with what can be passed
    # basically just allows all possible chars for everything as long as it meets expected format

    __fetch_regexp = re.compile(
        r"^fetch\(\"(?P<url>(?:http|https):\/\/.+)\", {\n  \"headers\": (?P<headers>{(?:.|\n)+}),\n  "
        r"(?:\"referrer\": \"(?P<referrer>.+)\",\n  |)\"referrerPolicy\": \"(?P<referrer_policy>.+)\",\n"
        r"(?:  \"body\": (?:\"|)(?P<body>.+?)(?:\"|),\n|)  \"method\": \"(?P<method>[A-Z]+)\",\n  (?:.|\n)+}\);"
    )

    def __init__(self):
        super().__init__()
        self.add_argument("-i", "--input", default=None, help="Input Directory")
        self.add_argument("-o", "--output", default=None, help="Output Directory")
        self.add_argument("--no-headers", action="store_true", help="Removes all headers from the operation")
        self.add_argument("--no-cookies", action="store_true", help="Removes all cookies from the operation")
        args = self.parse_args()

        # resolves path
        self.__input = (Path(args.i) if args.input else Path.cwd()).resolve()
        self.__output = (Path(args.o) if args.output else Path.cwd()).resolve()
        self.__no_headers = args.no_headers
        self.__no_cookies = args.no_cookies

        # dynamic tings from here on out
        self.__classes = {}
        # class: Class()
        self.__methods = {}
        # file: Method()
        self.__has_written = False

    def write(self):
        if not self.has_written:
            # handle local files
            self.parse_directory(self.input)

            # add non-local files and write python files
            for class_, class_obj in self.__classes.items():
                # create directories
                if self.output.name == class_:
                    # ex. class is named "autorequests" and output folder is named "autorequests"
                    class_folder = self.output
                else:
                    class_folder = self.output / class_
                    # add methods from class folder
                    if class_folder.exists():
                        self.parse_directory(class_folder)
                    else:
                        class_folder.mkdir(parents=True)
                with (class_folder / "main.py").open(mode="w") as py:
                    py.write(class_obj.code())

            # move local files into class folder
            for file, method in self.__methods.items():
                if self.output.name != method.class_name:
                    file.rename(self.output / method.class_name / file.name)
            self.__has_written = True

    def print_results(self):
        if len(self.classes) == 0:
            print("No fetches could be located.")
            return
        if not self.has_written:
            print("Modules haven't been written to the filesystem yet.")
            return
        num_classes = len(self.classes)
        num_methods = len(self.methods)
        classes_noun = "classes" if num_classes > 1 else "class"
        methods_noun = "methods" if num_methods > 1 else "method"
        print(f"Successfully wrote {num_classes} {classes_noun} with a total of {num_methods} {methods_noun}.")

    def is_fetch(self, fetch: str) -> bool:
        return self.__fetch_regexp.search(fetch) is not None

    def parse_fetch(self, fetch: str) -> Method:
        """
        Parses a fetch that should follow this format

        fetch(<URL>, {
          "headers": <HEADERS>,
          "referrer": <REFERRER>,  # optional
          "referrerPolicy": <REFERRER-POLICY>,  # might be optional
          "body": <BODY>,
          "method": <METHOD>,
          "mode": <MODE>
        });
        """
        match = self.__fetch_regexp.search(fetch)
        groups = match.groupdict()

        headers = json.loads(match["headers"])
        # referer is spelled wrong in the HTTP header
        # referrer policy is not
        if groups.get("referer"):
            headers["referer"] = groups["referrer"]
        if groups.get("referrer_policy"):
            headers["referrer-policy"] = groups["referrer_policy"]

        cookies_string = headers.pop("cookie") if "cookie" in headers else ""
        cookies = {}
        
        if self.__no_headers:
            headers = {}

        if not self.__no_cookies and cookies_string:
            for cookie in cookies_string.split("; "):
                equal_split = cookie.split("=")
                key = equal_split.pop(0)
                value = "=".join(equal_split)
                cookies[key] = value

        method = groups["method"]
        url = URL(groups["url"])
        body = Body(groups["body"] or "")

        return Method(method=method,
                      url=url,
                      body=body,
                      headers=headers,
                      cookies=cookies,
                      )

    def parse_directory(self, directory: Path):
        if not directory.exists():
            return
        for file in directory.glob("*.txt"):
            text = file.read_text(encoding="utf8", errors="ignore")
            if not self.is_fetch(text):
                continue
            method = self.parse_fetch(text)
            class_name = method.class_name
            self.__classes.setdefault(class_name, Class(class_name))
            self.__classes[class_name].add_method(method)
            self.__methods[file] = method

    @property
    def has_written(self):
        return self.__has_written

    @property
    def input(self) -> Path:
        return self.__input

    @property
    def output(self) -> Path:
        return self.__output

    @property
    def classes(self) -> dict:
        return self.__classes

    @property
    def methods(self) -> dict:
        return self.__methods


def main():
    handler = FetchHandler()
    handler.write()
    handler.print_results()


if __name__ == "__main__":
    main()
