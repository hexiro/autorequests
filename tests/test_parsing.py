from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from autorequests.parsing.fetch import parse_fetch
from autorequests.parsing.powershell import parse_powershell
from .common.fetch_examples import fetch_samples
from .common.powershell_examples import powershell_samples

if TYPE_CHECKING:
    from autorequests.lib import Method


@pytest.mark.parametrize("sample,expected", list(powershell_samples.items()))
def test_parse_powershell_to_method(sample: str, expected: Method) -> None:
    assert parse_powershell(sample) == expected


@pytest.mark.parametrize("sample,expected", list(fetch_samples.items()))
def test_parse_fetch_to_method(sample: str, expected: Method) -> None:
    assert parse_fetch(sample) == expected
