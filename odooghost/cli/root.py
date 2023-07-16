import typing as t
from pathlib import Path

import typer

from odooghost import __version__
from odooghost.context import ctx

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def setup(
    working_dir: t.Annotated[
        Path,
        typer.Argument(
            ...,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ]
) -> None:
    """
    Setup OdooGhost environment
    """
    if not working_dir.exists():
        working_dir.mkdir()
    elif working_dir.exists() and any(working_dir.iterdir()):
        print("Directory should be empty !")
    ctx.setup(version=__version__, working_dir=working_dir)


@cli.callback()
def callback() -> None:
    """
    OdooGhost make Odoo development easy
    """
    pass
