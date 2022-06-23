from __future__ import annotations

import json

from .commons import parse_url_encoded


def parse_body(
    body: str | None,
) -> tuple[dict[str, str] | None, dict[str, str] | None, dict[str, tuple[str, ...]] | None]:
    data: dict[str, str] | None = None
    json_: dict[str, str] | None = None
    files: dict[str, tuple[str, ...]] | None = None

    if not body:
        return data, json_, files
    else:
        body = fix_escape_chars(body)
        body = standardize_newlines(body)

    def is_multipart_form_data() -> bool:
        return "------WebKitFormBoundary" in body

    def is_urlencoded() -> bool:
        if not body or "=" not in body:
            return False
        return all(item.count("=") > 0 for item in body.split("&"))

    def is_json() -> bool:
        if not body:
            return False
        try:
            json.loads(body)
            return True
        except json.JSONDecodeError:
            return False

    if is_multipart_form_data():
        data, files = parse_multipart_form_data(body)
    elif is_urlencoded():
        data = parse_urlencoded(body)
    elif is_json():
        json_ = parse_json(body)
    return data, json_, files


def fix_escape_chars(body: str) -> str:
    """
    replaces escaped \\ followed by a letter to the appropriate char
    ignore/replace are kind of just guesses at what i think would be best
    if there is a more logical reason to use something else LMK!
    (ex. "\\t" --> "\t")
    """
    return body.encode(encoding="utf8", errors="ignore").decode(encoding="unicode_escape", errors="replace")


def standardize_newlines(body: str) -> str:
    """
    standardize newlines to \n
    (ex. "\r\n" --> "\n")
    """
    return "\n".join(body.splitlines())


def parse_json(self) -> dict[str, str] | None:
    return json.loads(self.body)


def parse_urlencoded(body: str) -> dict[str, str] | None:
    return parse_url_encoded(body)


def parse_multipart_form_data(body: str) -> tuple[dict[str, str] | None, dict[str, tuple[str, ...]] | None]:
    # let's all take a moment and pray for whoever has to refactor this (me probably)

    data: dict[str, str] = {}
    files: dict[str, tuple[str, ...]] = {}

    # it's too large to try and put raw file content in python file
    placeholder_data = 'open("file.raw", "rb")'

    def parse_details_dict(details: str) -> dict[str, str]:
        details_dict: dict[str, str] = {}
        for line in details.splitlines():
            if ": " not in line:
                continue
            key, value = line.split(": ", maxsplit=1)
            details_dict[key] = value
        return details_dict

    try:
        boundary, body = body.split("\n", maxsplit=1)
        body = body.rstrip("--")
    except ValueError:
        return None, None
    for item in body.split(boundary):
        # remove leading & trailing /n
        item = item.strip("\n")
        if not item:
            continue
        # get two main details
        item_split = item.split("\n\n", maxsplit=1)
        details = item_split.pop(0)
        content = item_split.pop() if item_split else ""

        details_dict = parse_details_dict(details)
        content_disposition = details_dict.get("Content-Disposition")
        if not content_disposition:
            continue
        # get filename && name
        content_disposition_dict: dict[str, str] = {}
        for detail in content_disposition[11:].split("; "):
            key, value = detail.split("=", maxsplit=1)
            value = value[1:-1]
            content_disposition_dict[key] = value

        if "name" not in content_disposition_dict:
            continue
        name = content_disposition_dict["name"]
        if "filename" not in content_disposition_dict:
            data[name] = content
            continue
        # if it has a filename it's a file
        filename = content_disposition_dict["filename"]
        if "Content-Type" not in details_dict:
            files[name] = (filename, placeholder_data)
            continue
        content_type = details_dict["Content-Type"]
        files[name] = (filename, placeholder_data, content_type)
    return (data or None), (files or None)
