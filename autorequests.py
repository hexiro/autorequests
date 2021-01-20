import os
import os.path
import sys
from re import sub
from json import loads

from urllib.parse import urlparse
from urllib.parse import unquote


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


def find_similarities(_list: list):
    if len(_list) == 1:
        return _list[0]
    _list = [item.lower() for item in _list]
    for letter_num in range(len(_list[0])):
        if not all([item.startswith(_list[0][:letter_num + 1]) for item in _list]):
            if letter_num == 0:
                return
            return _list[0][:letter_num]


class AutoRequest:

    def __init__(self):
        self.functions = [
            {
                "name": "__init__",
                "params": ["self"],
                "code": [
                    "self.session = requests.Session()"
                ],
            }
        ]

    def add_function(self, fetch):

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
        _dict["code"] = ""
        _dict["params"] = ["self"]
        _dict["method"] = _dict["method"].lower()

        url = fetch.split("\"")[1]
        url_parsed = urlparse(unquote(url))
        netloc_split = url_parsed.netloc.split(".")
        _dict["domain_name"] = url_parsed.netloc.split(".")[len(netloc_split)-2]
        parsed_url = f"{url_parsed.scheme}://{url_parsed.netloc}{url_parsed.path}"
        _dict["url"] = parsed_url

        # try and find good function name
        reversed_split = parsed_url.replace('.', '/').split('/')[::-1]
        for subdir in reversed_split:
            if len(subdir) == 0:
                continue
            try:
                float(subdir)
                continue
            except ValueError:
                pass
            _dict["name"] = sub(r"[-/\\?|{}\[\]()<>!@#$%^&*+=\"',.`~:;]", "", subdir)
            break
        else:
            _dict["name"] = sub(r"[-/\\?|{}\[\]()<>!@#$%^&*+=\"',.`~:;]", "", reversed_split[-1])

        if "?" in url:
            query_dict = {}
            query_url = url.replace("?", "&").split("&")
            del query_url[0]
            for query in query_url:
                key, value = query.split("=")
                query_dict[key] = value
            _dict["query"] = query_dict
        else:
            _dict["query"] = {}

        headers = _dict["headers"]
        unique_headers = {}
        for key, value in headers.items():
            if key.lower() in http_headers:
                continue
            unique_headers[key] = value
        _dict["unique_headers"] = unique_headers

        _dict["cookies"] = {}
        if "cookie" in headers.keys():
            for cookie in headers["cookie"].split(";"):
                try:
                    key, value = cookie.split("=")
                except ValueError:
                    key = cookie.split("=")[0]
                    value = ""
                _dict["cookies"][key] = value
            del _dict["headers"]["cookie"]
        if _dict.get("body") is not None:
            if headers.get("content-type") != "application/json":
                new_body = {}
                for pair in _dict["body"].split("&"):
                    key, value = pair.split("=")
                    new_body[key] = value
                _dict["body"] = new_body
        else:
            _dict["body"] = {}

        self.functions.append(_dict)
        return _dict

    def format_dict(self, _dict):
        dict_str = "{\n"
        for key, value in _dict.items():
            value = unquote(str(value))
            if isinstance(value, int):
                _value = int(value)
            elif isinstance(value, dict):
                _value = value
            elif value in ["True", "False", "None"]:
                _value = value
            elif value.startswith("[") and value.endswith("]"):
                _value = eval(value)
            else:
                _value = f"\"{value}\""
            dict_str += f"\"{key}\": {_value},\n"
        dict_str += "}"
        return dict_str

    def final(self, class_name):
        code = \
            "import requests\n" \
            "\n" \
            "\n" \
            "# Code generated from Node.js Fetches\n" \
            f"class {class_name}:\n" \
            "\n"

        protocol = "https" if self.functions[1]["url"].startswith("https") else "http"
        urls = [_dict["url"].split("://")[1] for _dict in self.functions if "url" in _dict]
        urls_match = find_similarities(urls)
        if urls_match:
            self.functions[0]["code"].append(f"self.url = \"{protocol}://{urls_match}\"")
            for func_num in range(len(self.functions)-1):  # +1-1 to ignore `init` function
                num = func_num + 1
                function_dict = self.functions[num]
                self.functions[num]["url"] = "{self.url}" + f"{function_dict['url'][len(protocol + urls_match)+3:]}"

        all_cookies = {}
        compatible_cookies = {}
        for function in self.functions:
            if "cookies" not in function:
                continue
            all_cookies.update(function["cookies"])
        for key, value in all_cookies.items():
            for func_num in range(len(self.functions)-1):
                num = func_num + 1
                if not self.functions[num]["cookies"].get(key) == value:
                    break
            else:
                compatible_cookies[key] = value
        if len(compatible_cookies) > 0:
            session_cookies = True
            self.functions[0]["code"].append("self.session.cookies.update({")
            lines = self.format_dict(compatible_cookies).splitlines()
            # function needs modifications - could be improved upon.
            del lines[0]
            lines[-1] += ")"
            for line in lines:
                self.functions[0]["code"].append(line)
        else:
            session_cookies = False

        all_headers = {}
        compatible_headers = {}
        for function in self.functions:
            if "headers" not in function:
                continue
            all_headers.update(function["unique_headers"])
        for key, value in all_headers.items():
            for func_num in range(len(self.functions)-1):
                num = func_num + 1
                if not self.functions[num]["headers"].get(key) == value:
                    break
            else:
                compatible_headers[key] = value
        if len(compatible_headers) > 0:
            session_headers = True
            self.functions[0]["code"].append("self.session.headers.update({")
            lines = self.format_dict(compatible_headers).splitlines()
            # function needs modifications - could be improved upon.
            del lines[0]
            lines[-1] += ")"
            for line in lines:
                self.functions[0]["code"].append(line)
        else:
            session_headers = False

        indent = " " * 4
        extra_indent = indent * 2
        for function_dict in self.functions:
            function_code = function_dict["code"]
            if function_dict["name"] != "__init__":
                # check for f string needed
                url = function_dict["url"]
                if "{" in url:
                    function_code += f"return self.session.{function_dict['method']}(f\"{url}\""
                else:
                    function_code += f"return self.session.{function_dict['method']}(\"{url}\""
                if function_dict["query"] != {}:
                    function_code += ", params="
                    function_code += self.format_dict(function_dict["query"])

                if function_dict.get("body"):
                    if "application/json" in function_dict.get("headers", {}).get("content-type"):
                        function_code += f", json="
                    else:
                        function_code += f", data="
                    function_code += self.format_dict(function_dict["body"])

                if function_dict.get("unique_headers"):
                    headers = function_dict["unique_headers"]
                    if session_headers:
                        headers = {x: headers[x] for x in set(headers) - set(compatible_headers)}
                    if headers != {}:
                        function_code += ", headers="
                        function_code += self.format_dict(headers)

                if function_dict.get("cookies"):
                    cookies = function_dict["cookies"]
                    if session_cookies:
                        cookies = {x: cookies[x] for x in set(cookies) - set(compatible_cookies)}
                    if cookies != {}:
                        function_code += ", cookies="
                        function_code += self.format_dict(cookies)

                function_code += ").json()"
                function_code = function_code.splitlines()
            name = function_dict["name"]
            params = "".join(function_dict["params"])
            code += f"{indent}def {name}({params}):\n"
            for line in function_code:
                if line.startswith("}") and line.endswith("{"):
                    code += f"{indent}{line}\n{indent}"
                elif line.startswith("}"):
                    code += f"{indent}{line}\n"
                elif line.endswith("{") or line.endswith(","):
                    code += f"{extra_indent}{line}\n{indent}"
                else:
                    code += f"{extra_indent}{line}\n"
            code += "\n"
        with open(f"{os.getcwd()}/{class_name}/main.py", "w") as py:
            py.write(code)


if __name__ == "__main__":
    autorequest = AutoRequest()
    local_files = [file for file in os.listdir() if file.endswith(".txt")]
    if len(local_files) == 0:
        exit()
    for file in local_files:
        autorequest.add_function(open(file, "r").read())
    if len(sys.argv) > 1:
        class_name = sys.argv[1]
    else:
        domain_names = [autorequest.functions[num+1]["domain_name"] for num in range(len(autorequest.functions)-1)]
        similarities = find_similarities(domain_names)
        if similarities:
            class_name = sub(r"[\\/:*?\"<>|]", "", similarities).capitalize()
        else:
            class_name = sub(r"[\\/:*?\"<>|]", "", domain_names[0]).capitalize()

    if not os.path.exists(class_name):
        os.mkdir(class_name)
    else:
        non_local_files = [f"{os.getcwd()}\\{class_name}\\{file}" for file in os.listdir(f"{os.getcwd()}\\{class_name}") if file.endswith(".txt")]
        for file in non_local_files:
            autorequest.add_function(open(file, "r").read())
    for file in local_files:
        os.rename(f"{file}", f"{class_name}\\{file}")
    autorequest.final(class_name)
