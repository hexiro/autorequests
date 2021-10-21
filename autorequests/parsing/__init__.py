from typing import Optional

from .fetch import parse_fetch_to_method
from .powershell import parse_powershell_to_method
from ..lib import Method

__all__ = ("parse_to_method",)


def parse_to_method(text: str) -> Optional[Method]:
    return parse_fetch_to_method(text) or parse_powershell_to_method(text)
