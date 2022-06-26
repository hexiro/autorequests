from dataclasses import dataclass, field
import sys

from autorequests.commons import format_dict

opts = {}

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
class ParsedInput:
    method: str
    url: str
    headers: dict[str, str] | None
    cookies: dict[str, str] | None
    params: dict[str, str] | None
    data: dict[str, str] | None
    json: dict[str, str] | None
    files: dict[str, tuple[str, ...]] | None

    def generate_code(self, *, sync: bool, httpx: bool, no_headers: bool, no_cookies: bool) -> str:

        method = self.method.lower()
        url = repr(self.url)

        request_data = {
            "headers": self.headers if not no_headers else None,
            "cookies": self.cookies if not no_cookies else None,
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
        elif not sync and httpx:
            return ASYNC_HTTPX.format(method=method, url=url, define_data=define_data, pass_data=pass_data)
        else:
            return ASYNC_AIOHTTP.format(method=method, url=url, define_data=define_data, pass_data=pass_data)

    def define_request_data(self, request_data: dict[str, dict[str, str] | dict[str, tuple[str, ...]] | None]) -> str:
        defined: str = ""
        for key, value in request_data.items():
            if not value:
                continue
            defined += f"{key} = {format_dict(value)}\n"
        defined = defined.rstrip("\n")
        return defined

    def pass_request_data(self, request_data: dict[str, dict[str, str] | dict[str, tuple[str, ...]] | None]) -> str:
        pass_list: list[str] = []
        for key, value in request_data.items():
            if not value:
                continue
            pass_list.append(f"{key}={key}")
        if not pass_list:
            return ""
        return ", ".join(pass_list)
