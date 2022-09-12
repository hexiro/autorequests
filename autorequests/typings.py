from __future__ import annotations

import typing as t

Data: t.TypeAlias = "dict[str, str]"  # type: ignore[name-defined]
JSON: t.TypeAlias = "dict[t.Any, t.Any] | list[t.Any]"  # type: ignore[name-defined]
Files: t.TypeAlias = "dict[str, bytes | tuple[str, bytes] | tuple[str, bytes, str]]"  # type: ignore[name-defined]
RequestData: t.TypeAlias = "dict[str, Data | JSON | Files | None]"  # type: ignore[name-defined]
