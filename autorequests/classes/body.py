import json


class Body:

    def __init__(self, body: str):
        # if you know a better solution for parsing double backslashes PLEASE LMK
        # not sure if i need more escape sequences :shrug:
        self.__body = str(body).replace("\\r\\n", "\n")\
                               .replace("\\n", "\n")\
                               .replace("\\r", "\n")\
                               .replace("\\t", "\t")\
                               .replace("\\", "")
        self.__data = {}
        self.__json = {}
        self.__files = {}

        if self.is_urlencoded:
            self.__parse_urlencoded()
        elif self.is_json:
            self.__parse_json()
        elif self.is_multipart_form_data:
            self.__parse_multipart_form_data()

    def __repr__(self):
        base = "<Body"
        if self.data:
            base += " data={self.data}"
        if self.json:
            base += " json={self.json}"
        if self.files:
            base += " files={self.files}"
        if base == "<Body":
            return "<Body data=None json=None files=None>"
        base += ">"
        # insecure string (because of self)
        return base.format(self=self)

    @property
    def body(self):
        return self.__body

    @property
    def data(self):
        return self.__data

    @property
    def json(self):
        return self.__json

    @property
    def files(self):
        return self.__files

    @property
    def is_json(self):
        try:
            json.loads(self.body)
            return True
        except json.JSONDecodeError as e:
            return False

    @property
    def is_urlencoded(self):
        if "=" not in self.body:
            return False
        for item in self.body.split("&"):
            if item.count("=") <= 0:
                return False
        return True

    @property
    def is_multipart_form_data(self):
        return "WebKitFormBoundary" in self.body

    def __parse_json(self):
        # sometimes body is "null" but we want our json to be a dict and not None
        json_ = json.loads(self.body)
        if json_ is not None:
            self.__json = json_

    def __parse_urlencoded(self):
        # urllib.parse.parse_qs doesn't work here btw
        # if a key doesn't have a value then it gets excluded with parse_qs
        for param in self.body.split("&"):
            if param.count("=") != 2:
                split = param.split("=")
                key = split.pop(0)
                value = "=".join(split)
            else:
                key, value = param.split("=")
            self.__data[key] = value

    def __parse_multipart_form_data(self):
        boundary = self.body.split("\n")[0]
        for item in self.body.replace("\r", "").split(boundary):
            # remove trailing /n
            item = item[:-1]
            # first item will be "" last will be "--" (bad data)
            if not item or item == "--":
                continue
            # get two main details
            separator = item.split("\n\n")
            details, content = separator[0], "\n\n".join(separator[1:])
            details_dict = {k: v for k, v in (detail.split(": ") for detail in details.splitlines() if detail)}
            content_disposition = details_dict.get("Content-Disposition")
            content_type = details_dict.get("Content-Type")
            if not content_disposition:
                continue
            # get filename && name
            content_disposition_dict = {}
            for detail in content_disposition[11:].split("; "):
                key, value = detail.split("=")
                value = value[1:-1]
                content_disposition_dict[key] = value
            name = content_disposition_dict.get("name")
            filename = content_disposition_dict.get("filename")

            if not name:
                pass
            # if it has a filename it's a file
            elif filename:
                self.__files[name] = (filename, content, content_type)
            # w/o filename it's just a normal piece of data
            else:
                self.__data[name] = content
