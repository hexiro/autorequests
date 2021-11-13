from typing import Optional

from .fetch import fetch_to_method
from .powershell import powershell_to_method
from ..lib import Method

__all__ = ("text_to_method",)


def text_to_method(text: str) -> Optional[Method]:
    return fetch_to_method(text) or powershell_to_method(text)
