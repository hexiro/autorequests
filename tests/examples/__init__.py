from __future__ import annotations  # noqa: FA101

from autorequests.request import Request

from .fetch_examples import fetch_examples  # noqa: F401
from .powershell_examples import powershell_examples  # noqa: F401

examples: dict[str, Request] = {}
