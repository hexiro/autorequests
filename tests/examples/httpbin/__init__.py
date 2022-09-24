from __future__ import annotations

from autorequests.request import Request

from .http_methods import httpbin_method_examples

httpbin_examples: dict[str, Request] = {**httpbin_method_examples}
