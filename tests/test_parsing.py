from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from autorequests.parsing.fetch import fetch_to_method
from autorequests.parsing.powershell import powershell_to_method
from .common.fetch_examples import fetch_samples
from .common.powershell_examples import powershell_samples

if TYPE_CHECKING:
    from autorequests.lib import Method


@pytest.mark.parametrize("sample,expected", list(powershell_samples.items()))
def test_parse_powershell_to_method(sample: str, expected: Method) -> None:
    assert powershell_to_method(sample) == expected


@pytest.mark.parametrize("sample,expected", list(fetch_samples.items()))
def test_parse_fetch_to_method(sample: str, expected: Method) -> None:
    assert fetch_to_method(sample) == expected
