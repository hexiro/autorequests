from __future__ import annotations

import typing as t

import rich_click as click

from .parsing import parse_input

if t.TYPE_CHECKING:
    import io

    from .request import Request

click.rich_click.STYLE_OPTION = "bold #4bff9f"
click.rich_click.STYLE_SWITCH = "bold blue"
click.rich_click.STYLE_METAVAR = "bold red"
click.rich_click.MAX_WIDTH = 75


def get_input() -> Request | None:
    """
    returns input from stdin
    """

    lines: list[str] = []
    line = input()

    while line and not line.isspace():
        lines.append(line)
        line = input()

    return parse_input("\n".join(lines))


@click.command()
# Meta Options
@click.option(
    "-f", "--file", type=click.File("r", encoding="utf-8", errors="replace"), help="Optional file to read input from."
)
@click.option("-c", "--copy", is_flag=True, default=False, help="Copy the output to the clipboard.")
# Generation Options
@click.option("-s/-a", "--sync/--async", is_flag=True, default=True, help="Generate synchronous or asynchronous code.")
@click.option("-h", "--httpx", is_flag=True, default=False, help="Use httpx library to make requests.")
@click.option("-nh", "--no-headers", is_flag=True, default=False, help="Don't include headers in the generated output.")
@click.option("-nc", "--no-cookies", is_flag=True, default=False, help="Don't include cookies in the generated output.")
def cli(file: io.TextIOWrapper, copy: bool, sync: bool, httpx: bool, no_headers: bool, no_cookies: bool) -> None:
    """
    Generate code to recreate a request from your browser.
    """
    from rich.console import Console
    from rich.syntax import Syntax

    console = Console(markup=True)

    parsed_input: Request | None = None

    if file:
        parsed_input = parse_input(file.read())
    else:
        console.print(
            """[#4bff9f][AutoRequests][/#4bff9f] Enter browser request data (and press enter when done)
[grey27 italic]*use --file if input data is too long*[/grey27 italic]"""
        )
        parsed_input = get_input()

    if not parsed_input:
        console.print(
            "[red]Invalid input. "
            "If you believe this is a mistake please report at: https://github.com/Hexiro/autorequests.[/red]"
        )
        return

    code = parsed_input.generate_code(sync=sync, httpx=httpx, no_headers=no_headers, no_cookies=no_cookies)

    console.print(Syntax(code, "python"))

    if copy:
        import pyperclip

        try:
            pyperclip.copy(code)
            console.print("[#4bff9f]Copied to clipboard.[/#4bff9f]")
        except pyperclip.PyperclipException:
            console.print(
                "[red]Copy functionality unavailable. Please view pyperclip documentation to use the --copy option.[/red]"
            )


if __name__ == "__main__":
    cli()
