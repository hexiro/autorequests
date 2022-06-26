from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, TypeAlias

Data: TypeAlias = "dict[str, str]"
JSON: TypeAlias = "dict[Any, Any] | list[Any]"
Files: TypeAlias = "dict[str, tuple[str, ...]]"
RequestData: TypeAlias = "dict[str, Data | JSON | Files | None]"
