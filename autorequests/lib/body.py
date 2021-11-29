import json
from typing import Optional, Dict, Tuple, Any, Generator

from ..utilities import fix_escape_chars, parse_url_encoded


class Body:
    def __init__(self, body: Optional[str] = None):
        if body:
            body = fix_escape_chars(body)
            # normalize newlines
            body = "\n".join(body.splitlines())
        self._body: str = body or ""
        self._data: Dict[str, str] = {}
        self._json: dict = {}
        # tuple of four items
        # 1. filename
        # 2. content
        # 3. content-type
        # 4. extra headers
        # (4th will never be used)
        self._files: Dict[str, Tuple[str, ...]] = {}

        # multipart is the most broad and obvious so it goes first
        # urlencoded is the simplest (hardest to check) so it goes last
        if self.body:
            if self.is_multipart_form_data:
                self._parse_multipart_form_data()
            elif self.is_json:
                self._parse_json()
            elif self.is_urlencoded:
                self._parse_urlencoded()

    def __repr__(self) -> str:
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

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Body):
            return NotImplemented
        return self.body == other.body

    def __hash__(self) -> int:
        return hash(self.body)

    @property
    def body(self) -> str:
        return self._body

    @property
    def data(self) -> Dict[str, str]:
        return self._data

    @property
    def json(self) -> dict:
        return self._json

    @property
    def files(self) -> Dict[str, Tuple[str, ...]]:
        return self._files

    @property
    def is_json(self) -> bool:
        if not self.body:
            return False
        try:
            json.loads(self.body)
            return True
        except json.JSONDecodeError:
            return False

    @property
    def is_urlencoded(self) -> bool:
        if not self.body or "=" not in self.body:
            return False
        return all(item.count("=") > 0 for item in self.body.split("&"))

    @property
    def is_multipart_form_data(self) -> bool:
        return "------WebKitFormBoundary" in self.body

    def _parse_json(self) -> None:
        # sometimes body is "null" but we want our json to be a dict and not None
        json_: Optional[dict] = json.loads(self.body)
        if json_ is not None:
            self._json.update(json_)

    def _parse_urlencoded(self) -> None:
        self._data.update(parse_url_encoded(self.body))

    def _parse_multipart_form_data(self) -> None:
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
            item_split = item.split("\n\n", maxsplit=1)
            details = item_split.pop(0)
            content = item_split.pop() if item_split else ""
            details_dict = self.details_dict(details)
            content_disposition = details_dict.get("Content-Disposition")
            if not content_disposition:
                continue
            # get filename && name
            content_disposition_dict: Dict[str, str] = {}
            for detail in content_disposition[11:].split("; "):
                key, value = detail.split("=", maxsplit=1)
                value = value[1:-1]
                content_disposition_dict[key] = value

            if "name" not in content_disposition_dict:
                return
            name = content_disposition_dict["name"]
            if "filename" not in content_disposition_dict:
                self._data[name] = content
                return
            # if it has a filename it's a file
            filename = content_disposition_dict["filename"]
            if "Content-Type" not in details_dict:
                self._files[name] = (filename, "...")
                return
            content_type = details_dict["Content-Type"]
            self._files[name] = (filename, "...", content_type)

    @staticmethod
    def details_dict(details: str) -> Dict[str, str]:
        details_dict: Dict[str, str] = {}
        for line in details.splitlines():
            if ": " not in line:
                continue
            key, value = line.split(": ", maxsplit=1)
            details_dict[key] = value
        return details_dict
