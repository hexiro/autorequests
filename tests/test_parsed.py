from __future__ import annotations
import ast
import itertools
from typing import TYPE_CHECKING

import pytest
from .examples import fetch_examples, powershell_examples

if TYPE_CHECKING:
    from autorequests.request import Request


@pytest.mark.parametrize("parsed_input", list(fetch_examples.values()) + list(powershell_examples.values()))
def test_parsed_input_generate_code(parsed_input: Request) -> None:
    num_arguments = len(["sync", "httpx", "no_headers", "no_cookies"])
    permutations = itertools.product([False, True], repeat=num_arguments)

    for sync, httpx, no_headers, no_cookies in permutations:
        code = parsed_input.generate_code(sync, httpx, no_headers, no_cookies)
        ast.parse(code)
