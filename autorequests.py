# parsing stdlib dependencies
from json import loads
from pprint import pprint
from urllib.parse import urlparse
from urllib.parse import unquote
import os
import os.path
import sys


http_headers = [
    "accept",
    "accept-encoding",
    "accept-language",
    "content-type",
    "cookie",
    "origin",
    "referer",
    "referrerpolicy",
    "sec-fetch-dest",
    "sec-fetch-mode",
    "sec-fetch-site",
    "sec-fetch-user",
    "upgrade-insecure-requests",
    "user-agent",
]


class AutoRequest:

    def __init__(self, class_name):
        self.class_name = class_name
        self.functions = [
            {
                "name": "__init__",
                "params": ["self"],
                "code": [
                    "self.session = requests.Session()"
                ],
            }
        ]

    def create_dict(self, fetch):

        # initial convert to dictionary
        _fetch_json = fetch.split("\", ")
        del _fetch_json[0]
        fetch_json = "".join(_fetch_json) \
            .replace("\n", "") \
            .replace(" ", "") \
            .replace("}\"", "}") \
            .replace("\"{", "{") \
            .replace(r"\"", "\"") \
            .split(");")[0]
        _dict = loads(fetch_json)

        headers = _dict["headers"]
        url = fetch.split("\"")[1]
        url_parsed = urlparse(unquote(url))
        parsed_url = f"{url_parsed.scheme}://{url_parsed.netloc}{url_parsed.path}"
        _dict["url"] = parsed_url

        if "?" in url:
            query_dict = {}
            for query in url.replace("?", "&").split("&"):
                key, value = query.split("=")
                query_dict[key] = value
            _dict["query"] = query_dict
        else:
            _dict["query"] = {}

        unique_headers = {}
        for key, value in headers.items():
            if key.lower() in http_headers:
                continue
            unique_headers[key] = value
        _dict["unique_headers"] = unique_headers

        reversed_split = parsed_url.replace('.', '/').split('/')[::-1]
        for subdir in reversed_split:

            if len(subdir) == 0:
                continue

            try:
                float(subdir)
            except ValueError:
                pass
            _dict["name"] = subdir
            break
        else:
            _dict["name"] = reversed_split[-1]

        _dict["cookies"] = {}
        if "cookie" in headers.keys():
            for cookie in headers["cookie"].split(";"):
                key, value = cookie.split("=")
                _dict["cookies"][key] = value
            del _dict["headers"]["cookie"]

        if _dict["body"] is not None:
            if headers["content-type"] != "application/json":
                _dict["body"] = {}
                for pair in _dict["body"].split("&"):
                    key, value = pair.split("=")
                    _dict["body"][key] = value
        else:
            _dict["body"] = {}

        return _dict

    def warning_comments(self, _dict):
        _headers = _dict["unique_headers"]
        if not _headers:
            return []
        comments = ["# possibly unique headers"]
        for key, value in _headers.items():
            if len(value) < 50:
                comments.append(f"# {key}: {value}")
            else:
                comments.append(f"# {key}: {value[:47]}...")
        if "cookie" not in _dict.keys():
            return comments
        cookies = _headers["cookie"]
        comments.append("# possibly important cookies")
        for cookie in sorted(cookies.split(";"), reverse=True):
            _semi_parsed = cookie.replace("=", ": ")
            if len(cookie) < 50:
                cookies.append(f"# {_semi_parsed}")
            else:
                cookies.append(f"# {_semi_parsed[:50]}...")
        return comments

    def format_dict(self, _dict, _indents=8):
        dict_str = "{\n"
        for key, value in _dict.items():
            if isinstance(value, int):
                _value = value
            elif value in ["True", "False", "None"]:
                _value = value
            else:
                _value = f"\"{value}\""
            dict_str += f"\"{key}\": {_value},\n"
        dict_str += "}"
        return dict_str

    def add_function(self, fetch, _indents=8):

        _dict = self.create_dict(fetch)
        function_name = _dict["name"]

        payload = {
            "name": function_name,
            "params": ["self"],
            "url": _dict["url"],
            "method": _dict['method'].lower(),
            "headers": _dict["headers"],
            "unique_headers": _dict["unique_headers"],
            "query": _dict["query"],
            "body": _dict["body"],
            "comments": self.warning_comments(_dict),
            "code": "",
        }

        # for comment in self.warning_comments(_dict):
        #     payload["code"] += f"{comment}\n"
        # 
        # payload["code"] += f"return self.session.{_dict['method'].lower()}(\"{_dict['url']}\""
        # if _dict["query"] != {}:
        #     payload["code"] += ", params="
        #     payload["code"] += self.format_dict(_dict["query"])
        # 
        # if _dict["body"] != {}:
        #     if "application/json" in _dict["headers"]["content-type"]:
        #         payload["code"] += f", json="
        #     else:
        #         payload["code"] += f", data="
        #     payload["code"] += self.format_dict(_dict["body"])
        # 
        # if _dict["unique_headers"] != {}:
        #     payload["code"] += ", headers="
        #     payload["code"] += self.format_dict(_dict["unique_headers"])
        # payload["code"] += ").json()"
        # payload["code"] = payload["code"].splitlines()
        self.functions.append(payload)
        return payload

    def match_api_url(self):
        protocols = [_dict["url"].split("://")[0] for _dict in self.functions if _dict.get("url", None) is not None]
        urls = [_dict["url"].split("://")[1] for _dict in self.functions if _dict.get("url", None) is not None]
        for protocol_num in range(len(protocols)):
            if protocols[protocol_num] != protocols[0]:
                common_protocol = "http"
                break
        else:
            common_protocol = "https"
        for letter_num in range(len(urls[0])):
            if not all([url.startswith(urls[0][:letter_num+1]) for url in urls]):
                final_num = letter_num
                break
        # ignore this final_num will always be defined
        if final_num != 0:
            self.functions[0]["code"].append(f"self.url = \"{common_protocol}://{urls[0][:final_num]}\"")
            final_num += len(f"{common_protocol}://")
            for func_num in range(len(self.functions)-1):  # +1-1 to ignore `init` function
                num = func_num + 1
                function_dict = self.functions[num]
                self.functions[num]["url"] = "{self.url}" + f"{function_dict['url'][final_num:]}"
        print(self.functions[0])

    def final(self):
        code = \
            "import requests\n" \
            "\n" \
            "\n" \
            "# Code generated from Node.js Fetches\n" \
            f"class {self.class_name}:\n" \
            "\n"
        indent = "    "
        extra_indent = "        "
        for func_num in range(len(self.functions)):
            function_dict = self.functions[func_num]
            function_code = function_dict["code"]
            print(function_code)
            if func_num != 0:
                for comment in self.warning_comments(function_dict):
                    function_code += f"{comment}\n"
                # check for f string needed
                url = function_dict["url"]
                if "{" in url:
                    function_code += f"return self.session.{function_dict['method']}(f\"{url}\""
                else:
                    function_code += f"return self.session.{function_dict['method']}(\"{url}\""
                if function_dict["query"] != {}:
                    function_code += ", params="
                    function_code += self.format_dict(function_dict["query"])

                if function_dict["body"] != {}:
                    if "application/json" in function_dict["headers"]["content-type"]:
                        function_code += f", json="
                    else:
                        function_code += f", data="
                    function_code += self.format_dict(function_dict["body"])

                if function_dict["unique_headers"] != {}:
                    function_code += ", headers="
                    function_code += self.format_dict(function_dict["unique_headers"])
                function_code += ").json()"
                function_code = function_code.splitlines()
            name = function_dict["name"]
            params = "".join(function_dict["params"])
            code += f"{indent}def {name}({params}):\n"
            for line in function_code:
                if line.endswith("{") or line.endswith(","):
                    code += f"{extra_indent}{line}\n{indent}"
                elif line.startswith("}"):
                    # here we only need indent because it already has an extra four spaces
                    code += f"{indent}{line}\n"
                else:
                    code += f"{extra_indent}{line}\n"
            code += "\n"
        with open(f"{os.getcwd()}/{self.class_name}/main.py", "w") as py:
            py.write(code)


if __name__ == "__main__":
    name = sys.argv[1]
    autorequest = AutoRequest(name)
    files = []
    if not os.path.exists(name):
        os.mkdir(name)
    else:
        [files.append(f"{os.getcwd()}\\{name}\\{file}") for file in os.listdir(f"{os.getcwd()}\\{name}") if file.endswith(".txt")]
    [files.append(file) for file in os.listdir() if file.endswith(".txt")]
    for file in files:
        autorequest.add_function(open(file, "r").read())
        if "\\" not in file:
            os.rename(f"{file}", f"{name}\\{file}")
    print(autorequest.match_api_url())
    print(autorequest.final())
    pprint(autorequest.functions)
