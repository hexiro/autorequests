from __future__ import annotations

import typing as t

Data: t.TypeAlias = "dict[str, str]"
JSON: t.TypeAlias = "dict[t.Any, t.Any] | list[t.Any]"
Files: t.TypeAlias = "dict[str, bytes | tuple[str, bytes] | tuple[str, bytes, str]]"
RequestData: t.TypeAlias = "dict[str, Data | JSON | Files | None]"
