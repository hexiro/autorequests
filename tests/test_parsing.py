from __future__ import annotations

import typing as t

import pytest

from autorequests.parsing import parse_fetch, parse_powershell

from .examples import fetch_examples, powershell_examples

if t.TYPE_CHECKING:
    from autorequests.request import Request


@pytest.mark.parametrize("sample,expected", list(powershell_examples.items()))
def test_parse_powershell_to_method(sample: str, expected: Request) -> None:
    assert parse_powershell(sample) == expected


@pytest.mark.parametrize("sample,expected", list(fetch_examples.items()))
def test_parse_fetch_to_method(sample: str, expected: Request) -> None:
    assert parse_fetch(sample) == expected
