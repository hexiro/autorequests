from autorequests.parsing.fetch import parse_fetch_to_method
from autorequests.parsing.powershell import parse_powershell_to_method
from .common.fetch_examples import fetch_examples
from .common.powershell_examples import powershell_examples


def test_parse_powershell_to_method():
    for example, method in powershell_examples.items():
        assert parse_powershell_to_method(example) == method


def test_parse_fetch_to_method():
    for example, method in fetch_examples.items():
        assert parse_fetch_to_method(example) == method
