"""Handles code generation and interaction with the parsed input"""
from __future__ import annotations

import sys
import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    from .typings import JSON, Data, Files, RequestData

from .commons import format_json_like, format_string

opts: dict[str, bool] = {}
if sys.version_info >= (3, 10):
    opts["slots"] = True


SYNC_REQUESTS = """{define_data}
resp = requests.{method}({url}, {pass_data})
"""

SYNC_HTTPX = """{define_data}
resp = httpx.{method}({url}, {pass_data})
"""

ASYNC_AIOHTTP = """{define_data}
async with aiohttp.ClientSession() as session:
    resp = await session.{method}({url}, {pass_data})
"""

ASYNC_HTTPX = """{define_data}
async with httpx.AsyncClient({pass_data}) as client:
    resp = await client.{method}({url})
"""


@dataclass(**opts)
class Request:
    method: str
    url: str
    headers: dict[str, str] | None
    cookies: dict[str, str] | None
    params: dict[str, str] | None
    data: Data | None
    json: JSON | None
    files: Files | None

    def generate_code(self, sync: bool, httpx: bool, no_headers: bool, no_cookies: bool) -> str:

        method = self.method.lower()
        url = format_string(self.url)

        request_data = {
            "headers": None if no_headers else self.headers,
            "cookies": None if no_cookies else self.cookies,
            "params": self.params,
            "data": self.data,
            "json": self.json,
            "files": self.files,
        }


        define_data = self.define_request_data(request_data)
        pass_data = self.pass_request_data(request_data)

        if sync and httpx:
            return SYNC_HTTPX.format(method=method, url=url, define_data=define_data, pass_data=pass_data)
        elif sync:
            return SYNC_REQUESTS.format(method=method, url=url, define_data=define_data, pass_data=pass_data)
        elif httpx:
            return ASYNC_HTTPX.format(method=method, url=url, define_data=define_data, pass_data=pass_data)
        else:
            return ASYNC_AIOHTTP.format(method=method, url=url, define_data=define_data, pass_data=pass_data)

    def define_request_data(self, request_data: RequestData) -> str:
        defined: str = "".join(
            f"{key} = {format_json_like(value)}\n"
            for key, value in request_data.items()
            if value
        )

        defined = defined.rstrip("\n")
        return defined

    def pass_request_data(self, request_data: RequestData) -> str:
        pass_list: list[str] = [
            f"{key}={key}" for key, value in request_data.items() if value
        ]

        return ", ".join(pass_list) if pass_list else ""
