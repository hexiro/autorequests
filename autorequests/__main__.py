from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import io

import rich_click as click


click.rich_click.STYLE_OPTION = "bold magenta"
click.rich_click.STYLE_SWITCH = "bold blue"
click.rich_click.STYLE_METAVAR = "bold red"
click.rich_click.MAX_WIDTH = 75


def get_lines():
    import sys

    """
    returns a generator of lines from stdin
    """
    for line in sys.stdin:
        line = line.rstrip()
        if line in ["", "}", ")"]:
            return
        yield line


@click.command()
@click.option("-f", "--file", type=click.File("r"), help="Optional file to read from")
@click.option("-s/-a", "--sync/--async", is_flag=True, default=True, help="Generate synchronous or asynchronous code.")
@click.option("-h", "--httpx", is_flag=True, default=False, help="Use httpx library to make requests.")
@click.option("-nh", "--no-headers", is_flag=True, default=False, help="Don't include headers in the output.")
@click.option("-nc", "--no-cookies", is_flag=True, default=False, help="Don't include cookies in the output.")
def cli(file: io.TextIOWrapper, sync: bool, httpx: bool, no_headers: bool, no_cookies: bool) -> None:
    """
    Main entry point for the cli.
    """
    from rich.console import Console
    from rich.syntax import Syntax

    from .input import parse_input

    console = Console(markup=True)

    unparsed_input: str | None = None
    if file:
        unparsed_input = file.read()

    if unparsed_input is None:
        console.print("[magenta][AUTOREQUESTS][/magenta] Enter browser request data (and press enter when done):")
        unparsed_input = "\n".join(get_lines())

    parsed_input = parse_input(unparsed_input)

    if not parsed_input:
        console.print(
            "[red]Invalid input. "
            "If you believe this is a mistake please report at: https://github.com/Hexiro/autorequests.[/red]"
        )
        return

    code = parsed_input.generate_code(sync=sync, httpx=httpx, no_headers=no_headers, no_cookies=no_cookies)

    syntax = Syntax(code, "python")
    console.print(syntax)


if __name__ == "__main__":
    cli()
