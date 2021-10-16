import inspect as _inspect

from rich.syntax import Syntax

from ..utilities import indent


def inspect(cls):
    methods = [x for x in (getattr(cls, i) for i in dir(cls)) if _inspect.isfunction(x) and x.__name__ != "__init__"]
    signatures = []
    for method in methods:
        signature = f"def {method.__name__}{_inspect.signature(method)}:"
        doc = _inspect.getdoc(method)
        if doc:
            # add docstring
            signature += f"\n    \"\"\"\n{indent(doc)}\n    \"\"\""
        signatures.append(signature)
    return Syntax("\n\n".join(signatures), "python", theme="fruity")
