from __future__ import annotations

from .fetch import parse_fetch, is_fetch
from .powershell import parse_powershell, is_powershell

from ..request import Request

__all__ = ("parse_input", "parse_fetch", "parse_powershell", "is_fetch", "is_powershell")


def parse_input(text: str) -> Request | None:
    if is_fetch(text):
        return parse_fetch(text)
    if is_powershell(text):
        return parse_powershell(text)
    return None
