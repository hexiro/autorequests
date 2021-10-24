from typing import Any, Optional

# called a sentinel. more can be read here:
# https://www.python.org/dev/peps/pep-0661/
# https://en.wikipedia.org/wiki/Sentinel_value
_MISSING = object()


class Parameter:

    def __init__(self, name: str, *, default: Any = _MISSING, typehint: Any = _MISSING):
        self._name: str = name
        self._default: Any = default
        self._typehint: Any = typehint

    def __repr__(self):
        return f"<Parameter {self.code}>"

    def __str__(self):
        return self.code

    def __eq__(self, other):
        if not isinstance(other, Parameter):
            return NotImplemented
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

    @property
    def code(self):
        if self.typehint and self.default:
            return f"{self.name}: {self.typehint} = {self.default}"
        if self.typehint:
            return f"{self.name}: {self.typehint}"
        if self.default:
            return f"{self.name}={self.default}"
        return self.name

    @property
    def name(self):
        return self._name

    @property
    def typehint(self) -> Optional[str]:
        if self._typehint is _MISSING:
            return
        # typing module
        if hasattr(self._typehint, "_name"):
            return str(self._typehint)
        # built-in types
        if hasattr(self._typehint, "__name__"):
            return self._typehint.__name__

    @property
    def default(self) -> Optional[str]:
        if self._default is _MISSING:
            return
        return repr(self._default)
