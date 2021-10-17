import json
import urllib.parse
from typing import Optional, Dict, Tuple, Union


class Body:

    def __init__(self, body: Optional[str]):
        if body:
            # parse escape sequences :thumbs_up:
            # ignore/replace are kind of just guesses at what i think would be best
            # if there is a more logical reason to use something else LMK!
            body = (body
                    .encode(encoding="utf8", errors="ignore")
                    .decode(encoding="unicode_escape", errors="replace"))
            # replace line breaks with \n(s)
            body = "\n".join(body.splitlines())
        self._body: Optional[str] = body
        self._data: Dict[str, str] = {}
        self._json: Dict[str, str] = {}
        # tuple of four items
        # 1. filename
        # 2. content
        # 3. content-type
        # 4. extra headers
        self._files: Dict[str, Union[Tuple[str, str], Tuple[str, str, str]]] = {}

        # multipart is the most broad and obvious so it goes first
        if not body:
            pass
        elif self.is_multipart_form_data:
            self._parse_multipart_form_data()
        elif self.is_json:
            self._parse_json()
        # urlencoded is the simplest (hardest to check) so it goes last
        elif self.is_urlencoded:
            self._parse_urlencoded()

    def __repr__(self):
        base = "<Body"
        if self.body:
            if self.data:
                base += f" data={self.data}"
            if self.json:
                base += f" json={self.json}"
            if self.files:
                base += f" files={self.files}"
        if base == "<Body":
            return "<Body data=None json=None files=None>"
        return base + ">"

    @property
    def body(self):
        return self._body

    @property
    def data(self):
        return self._data

    @property
    def json(self):
        return self._json

    @property
    def files(self):
        return self._files

    @property
    def is_json(self):
        try:
            json.loads(self.body)
            return True
        except json.JSONDecodeError:
            return False

    @property
    def is_urlencoded(self):
        if "=" not in self.body:
            return False
        return all(item.count("=") > 0 for item in self.body.split("&"))

    @property
    def is_multipart_form_data(self):
        return "------WebKitFormBoundary" in self.body

    def _parse_json(self):
        # sometimes body is "null" but we want our json to be a dict and not None
        json_ = json.loads(self.body)
        if json_ is not None:
            self._json = json_

    def _parse_urlencoded(self):
        # urllib.parse.parse_qs doesn't work here btw
        # if a key doesn't have a value then it gets excluded with parse_qs
        # not sure if unquote_plus() would be better
        body = urllib.parse.unquote(self.body)
        for param in body.split("&"):
            key, value = param.split("=", maxsplit=1)
            self._data[key] = value

    def _parse_multipart_form_data(self):
        # let's all take a moment and pray for whoever has to refactor this (me probably)
        try:
            boundary, body = self.body.split("\n", maxsplit=1)
            body = body.rstrip("--")
        except ValueError:
            return
        for item in body.split(boundary):
            # remove leading & trailing /n
            item = item.strip("\n")
            if not item:
                continue
            # get two main details
            # try:
            item_split = item.split("\n\n", maxsplit=1)
            details = item_split.pop(0)
            content = item_split.pop() if item_split else ""
            details_dict = {k: v for k, v in
                            (line.split(": ", maxsplit=1) for line in details.splitlines() if ": " in line)}
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
                self._data[name] = content
            # if it has a filename it's a file
            elif content_type:
                self._files[name] = (filename, "...", content_type)
            else:
                self._files[name] = (filename, "...")
