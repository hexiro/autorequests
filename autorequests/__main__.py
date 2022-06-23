from __future__ import annotations
import itertools
import sys

import rich_click as click


__version__ = "1.1.1"


click.rich_click.STYLE_OPTION = "bold magenta"
click.rich_click.STYLE_SWITCH = "bold blue"
click.rich_click.STYLE_METAVAR = "bold red"
click.rich_click.MAX_WIDTH = 75


def get_lines():
    """
    returns a generator of lines from stdin
    """
    for line in sys.stdin:
        line = line.rstrip()
        if line in ["", "}", ")"]:
            return
        yield line


@click.command()
@click.argument("input", nargs=-1)
@click.option("-s/-a", "--sync/--async", is_flag=True, default=True, help="Generate synchronous or asynchronous code.")
@click.option("-h", "--httpx", is_flag=True, default=False, help="Use httpx library to make requests.")
def cli(input: tuple[str], sync: bool, httpx: bool) -> None:
    """
    Main entry point for the cli.
    """
    from rich.console import Console
    from rich.syntax import Syntax

    from .input import parse_input

    extra_lines = tuple(get_lines())

    data = "\n".join(input + extra_lines)

    parsed_input = parse_input(data)
    if not parsed_input:
        print("No parsed input.")
        return
    code = parsed_input.generate_code(sync=sync, httpx=httpx)

    console = Console()
    syntax = Syntax(code, "python")
    console.print(syntax)


if __name__ == "__main__":
    cli()
