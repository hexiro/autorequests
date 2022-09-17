from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    import io

import rich_click as click

click.rich_click.STYLE_OPTION = "bold #4bff9f"
click.rich_click.STYLE_SWITCH = "bold blue"
click.rich_click.STYLE_METAVAR = "bold red"
click.rich_click.MAX_WIDTH = 75


def get_input() -> str:
    """
    returns input from stdin
    """

    lines: list[str] = []
    line = input()

    while line and not line.isspace():
        lines.append(line)
        line = input()

    return "\n".join(lines)


@click.command()
# Meta Options
@click.option(
    "-f", "--file", type=click.File("r", encoding="utf-8", errors="replace"), help="Optional file to read input from."
)
@click.option("-c", "--copy", is_flag=True, default=False, help="Copy the output to the clipboard")
# Generation Options
@click.option("-s/-a", "--sync/--async", is_flag=True, default=True, help="Generate synchronous or asynchronous code.")
@click.option("-h", "--httpx", is_flag=True, default=False, help="Use httpx library to make requests.")
@click.option("-nh", "--no-headers", is_flag=True, default=False, help="Don't include headers in the output.")
@click.option("-nc", "--no-cookies", is_flag=True, default=False, help="Don't include cookies in the output.")
def cli(file: io.TextIOWrapper, copy: bool, sync: bool, httpx: bool, no_headers: bool, no_cookies: bool) -> None:
    """
    Generate code to recreate a request from your browser.
    """
    from rich.console import Console
    from rich.syntax import Syntax

    from .parsing import parse_input

    console = Console(markup=True)

    unparsed_input: str | None = None

    if file:
        unparsed_input = file.read()

    if unparsed_input is None:
        console.print("[#4bff9f][AutoRequests][/#4bff9f] Enter browser request data (and press enter when done):")
        unparsed_input = get_input()

    parsed_input = parse_input(unparsed_input)

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

        if not pyperclip.is_available():
            console.print(
                "[red]Copy functionality unavailable. Please view pyperclip documentation to use the --copy option.[/red]"
            )
            return

        pyperclip.copy(code)
        console.print("[#4bff9f]Copied to clipboard.[/#4bff9f]")


if __name__ == "__main__":
    cli()
