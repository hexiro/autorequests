import argparse
import ast
from pathlib import Path
from typing import List, Optional, Dict, Generator, Union

import rich
from rich.box import MINIMAL
from rich.syntax import Syntax
from rich.table import Table

from .lib import Class, Method
from .parsing import text_to_method
from .utilities import cached_property, indent

__version__ = "1.1.1"
__all__ = ("AutoRequests", "main", "__version__")

console = rich.get_console()


class AutoRequests:
    def __init__(
        self,
        *,
        input_path: Path,
        output_path: Path,
        return_text: bool = False,
        no_headers: bool = False,
        no_cookies: bool = False,
        parameters: bool = False,
    ):

        # params

        self._return_text: bool = return_text
        self._no_headers: bool = no_headers
        self._no_cookies: bool = no_cookies
        self._parameters: bool = parameters

        # dynamic
        self._input_path: Path = input_path
        self._output_path: Path = output_path
        self._input_methods: Dict[Path, Method] = {}
        self._output_classes: Dict[Path, Class] = {}

        self._methods: List[Method] = self.methods_from_path(self.input_path)
        self._classes: List[Class] = [
            Class(
                name=name,
                output_path=output_path,
                return_text=return_text,
                no_headers=no_headers,
                no_cookies=no_cookies,
                parameters=parameters,
            )
            for name in {method.class_name for method in self.methods}
        ]

        for cls in self.classes:
            if cls.folder != self.output_path:
                self.methods.extend(self.methods_from_path(cls.folder))

        for method in self.methods:
            cls: Optional[Class] = self.find_class(method.class_name)  # type: ignore[no-redef]
            if not cls:
                continue
            cls.add_method(method)
            method.class_ = cls

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} classes={self.classes!r}>"

    @property
    def return_text(self) -> bool:
        return self._return_text

    @property
    def no_headers(self) -> bool:
        return self._no_headers

    @property
    def no_cookies(self) -> bool:
        return self._no_cookies

    @property
    def parameters(self) -> bool:
        return self._parameters

    @property
    def input_path(self) -> Path:
        return self._input_path

    @property
    def output_path(self) -> Path:
        return self._output_path

    @property
    def input_methods(self) -> Dict[Path, Method]:
        return self._input_methods

    @property
    def output_classes(self) -> Dict[Path, Class]:
        return self._output_classes

    @cached_property
    def methods(self) -> List[Method]:
        return self._methods

    @cached_property
    def classes(self) -> List[Class]:
        return self._classes

    def class_output_path(self, cls: Class) -> Union[Path, Class]:
        if self.output_path.name != cls.name:
            return self.output_path / cls.name
        return cls

    def methods_from_path(self, path: Path) -> List[Method]:
        methods = []
        for file in self.files_from_path(path):
            text = file.read_text(encoding="utf8", errors="ignore")
            method = text_to_method(text)
            if method is None:
                continue
            methods.append(method)
            self.input_methods[file] = method
        return methods

    @property
    def top(self) -> str:
        return "import requests\n\n\n# Automatically generated by https://github.com/Hexiro/autorequests.\n\n"

    def write(self) -> None:
        for cls in self.classes:
            if not cls.folder.exists():
                cls.folder.mkdir()
            main_py = cls.folder / "main.py"
            main_py.write_text(data=self.top + cls.code, encoding="utf8", errors="strict")
            self.output_classes[main_py] = cls

    def move_input_files(self) -> None:
        for file, method in self.input_methods.items():
            class_name = method.class_name
            if self.output_path.name != class_name:
                file.rename(self.output_path / class_name / file.name)

    @staticmethod
    def files_from_path(path: Path) -> Generator[Path, None, None]:
        return path.glob("*.txt")

    def find_class(self, name: str) -> Optional[Class]:  # type: ignore[return]
        for cls in self.classes:
            if cls.name == name:
                return cls

    def main(self) -> None:
        self.write()
        self.print_results()
        self.move_input_files()

    def print_results(self) -> None:
        if not self.output_classes:
            print("No request data could be located.")
            return
        table = Table(box=MINIMAL, border_style="bold red")
        code = []
        for path, cls in self.output_classes.items():
            try:
                try:
                    ast.parse(cls.code)
                except SyntaxError as err:
                    err.msg = "invalid syntax in the code generated. is this worth reporting?"
                    raise
            except SyntaxError:
                console.print_exception()
                return

            name = path.parent.name
            table.add_column(f"[bold red]{name}[/bold red]")
            signatures_with_docstrings = [f"{method.signature}\n{indent(method.docstring)}" for method in cls.methods]
            code.append(Syntax("\n\n".join(signatures_with_docstrings), "python", theme="fruity"))
        table.width = 65 * len(code)
        table.add_row(*code)
        console.print(table)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default=None, help="Input Directory")
    parser.add_argument("-o", "--output", default=None, help="Output Directory")
    parser.add_argument("-v", "--version", action="store_true")
    parser.add_argument(
        "--return-text",
        action="store_true",
        help="Makes the generated method's responses return .text instead of .json()",
    )
    parser.add_argument("--no-headers", action="store_true", help="Removes all headers from the operation")
    parser.add_argument("--no-cookies", action="store_true", help="Removes all cookies from the operation")
    parser.add_argument(
        "--parameters",
        action="store_true",
        help="Replaces hardcoded params, json, data, etc with parameters that have default values",
    )
    args = parser.parse_args()

    if not args:
        parser.print_help()
        return
    if args.version:
        print(f"AutoRequests {__version__}")
        return

    input_path = Path.cwd()
    output_path = Path.cwd()
    if args.input:
        input_path = Path(args.input).resolve()
    if args.output:
        input_path = Path(args.output).resolve()

    auto_requests = AutoRequests(
        input_path=input_path,
        output_path=output_path,
        return_text=args.return_text,
        no_headers=args.no_headers,
        no_cookies=args.no_cookies,
        parameters=args.parameters,
    )
    auto_requests.main()


if __name__ == "__main__":
    main()
