from __future__ import annotations

import ast
import asyncio
import itertools
import typing as t

import aiohttp
import httpx
import pytest
import requests

from autorequests.parsing import parse_input

from .examples import fetch_examples, powershell_examples
from .examples.httpbin import httpbin_examples

if t.TYPE_CHECKING:
    from autorequests.request import Request


@pytest.mark.parametrize("req", list(fetch_examples.values()) + list(powershell_examples.values()))
def test_request_generate_code(req: Request) -> None:
    num_arguments = len(["sync", "httpx", "no_headers", "no_cookies"])
    permutations = itertools.product([False, True], repeat=num_arguments)

    for sync, use_httpx, no_headers, no_cookies in permutations:
        code = req.generate_code(sync, use_httpx, no_headers, no_cookies)
        ast.parse(code)


async def aexec_code(code: str) -> httpx.Response | aiohttp.ClientResponse:  # type: ignore[return]
    """
    References:
        https://stackoverflow.com/a/53255739/10830115
    """

    # Make an async function with the code and `exec` it
    func_body = "".join(f"\n {line}" for line in code.split("\n"))
    exec(f"async def __ex(): {func_body}\n return resp")

    try:
        # Get `__ex` from local variables, call it and return the result
        resp: httpx.Response | aiohttp.ClientResponse = await locals()["__ex"]()
        return resp
    except (httpx.NetworkError, aiohttp.ClientConnectionError):
        pytest.skip("Network unavailable")


def exec_code(code: str) -> httpx.Response | requests.Response:  # type: ignore[return]
    """
    References:
        https://stackoverflow.com/a/53255739/10830115
    """

    # Make a function with the code and `exec` it
    func_body = "".join(f"\n {line}" for line in code.split("\n"))
    exec(f"def __ex(): {func_body}\n return resp")

    try:
        # Get `__ex` from local variables, call it and return the result
        resp: httpx.Response | requests.Response = locals()["__ex"]()
        return resp
    except (httpx.NetworkError, requests.exceptions.ConnectionError):
        pytest.skip("Network unavailable")


@pytest.mark.parametrize("sample", httpbin_examples)
def test_request_httpbin(sample: str) -> None:

    request = parse_input(sample)
    assert request is not None

    num_arguments = len(["sync", "httpx"])
    permutations = itertools.product([False, True], repeat=num_arguments)

    responses: list[aiohttp.ClientResponse | httpx.Response | requests.Response] = []
    loop = asyncio.new_event_loop()

    for sync, use_httpx in permutations:
        code = request.generate_code(sync, use_httpx, no_headers=False, no_cookies=False)
        response: aiohttp.ClientResponse | httpx.Response | requests.Response
        if sync:
            response = exec_code(code)
            assert isinstance(response, (httpx.Response, requests.Response))
            responses.append(response)
        else:
            response = loop.run_until_complete(aexec_code(code))
            assert isinstance(response, (httpx.Response, aiohttp.ClientResponse))
            responses.append(response)

    print(responses)

    for response in responses:
        response.raise_for_status()
