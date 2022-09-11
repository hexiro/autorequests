from __future__ import annotations

from ..request import Request
from .fetch import is_fetch, parse_fetch
from .powershell import is_powershell, parse_powershell

__all__ = ("parse_input", "parse_fetch", "parse_powershell", "is_fetch", "is_powershell")


def parse_input(text: str) -> Request | None:
    if is_fetch(text):
        return parse_fetch(text)
    if is_powershell(text):
        return parse_powershell(text)
    return None
