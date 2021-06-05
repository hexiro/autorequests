import json
import urllib.parse

class Body:

    def __init__(self, body: str):
        body = str(body)
        # parse escape sequences :thumbs_up:
        # ignore/replace are kind of just guesses at what i think would be best
        # if there is a more logical reason to use something else LMK!
        body = body.encode(encoding="utf8", errors="ignore")\
                   .decode(encoding="unicode_escape", errors="replace")
        # replace line breaks with \n(s)
        body = "\n".join(body.splitlines())
        self.__body = body
        self.__data = {}
        self.__json = {}
        self.__files = {}

        # multipart is the most broad and obvious so it goes first
        if self.is_multipart_form_data:
            self.__parse_multipart_form_data()
        elif self.is_json:
            self.__parse_json()
        # urlencoded is the simplest (hardest to check) so it goes last
        elif self.is_urlencoded:
            self.__parse_urlencoded()

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
        # technically an insecure string (because of self)
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
        return "------WebKitFormBoundary" in self.body

    def __parse_json(self):
        # sometimes body is "null" but we want our json to be a dict and not None
        json_ = json.loads(self.body)
        if json_ is not None:
            self.__json = json_

    def __parse_urlencoded(self):
        # urllib.parse.parse_qs doesn't work here btw
        # if a key doesn't have a value then it gets excluded with parse_qs
        # not sure if unquote_plus() would be better
        body = urllib.parse.unquote(self.body)
        for param in body.split("&"):
            key, value = param.split("=", maxsplit=1)
            self.__data[key] = value

    def __parse_multipart_form_data(self):
        try:
            boundary, body = self.body.split("\n", maxsplit=1)
            body = body.rstrip("--")
        except ValueError:
            return
        for item in body.split(boundary):
            # remove leading & trailing /n
            if item.endswith("\n"):
                item = item[:-1]
            if item.startswith("\n"):
                item = item[1:]
            # get two main details
            try:
                details, content = item.split("\n\n")
                details = details.lstrip(boundary + "\n")
                details_dict = {k: v for k, v in
                                (line.split(": ", maxsplit=1) for line in details.splitlines() if ": " in line)}
            except ValueError:
                # bad data that wasn't caught earlier
                # this should never be reached, it's kind of just a safeguard in case the data is corrupted asf
                continue
            content_disposition = details_dict.get("Content-Disposition")
            content_type = details_dict.get("Content-Type")
            if not content_disposition:
                continue
            # get filename && name
            content_disposition_dict = {}
            for detail in content_disposition[11:].split("; "):
                key, value = detail.split("=", maxsplit=1)
                value = value[1:-1]
                content_disposition_dict[key] = value
            name = content_disposition_dict.get("name")
            filename = content_disposition_dict.get("filename")

            if not name:
                pass
            elif not filename:
                self.__data[name] = content
            # if it has a filename it's a file
            # tuple of four items
            # 1. filename
            # 2. content
            # 3. content-type
            # 4. extra headers
            elif content_type:
                self.__files[name] = (filename, content, content_type)
            else:
                self.__files[name] = (filename, content)
