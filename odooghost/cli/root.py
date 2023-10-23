import typing as t
from pathlib import Path

import typer
from loguru import logger

from odooghost import __version__, check_version
from odooghost.context import ctx

from . import config, stack

cli = typer.Typer(no_args_is_help=True)
cli.add_typer(config.cli, name="config")
cli.add_typer(stack.cli, name="stack")


@cli.command()
def version() -> None:
    """
    Print OdooGhost version
    """
    print(__version__)

    available_version, new_version = check_version()

    if available_version:
        print(
            "A new version may be available, you are on a "
            + __version__
            + " and the "
            + new_version
            + " is available. Please check for any security or major updates."
        )


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
    if ctx.check_setup_state():
        logger.error("OdooGhost already setup !")
        raise typer.Abort()
    if not working_dir.exists():
        working_dir.mkdir()
    elif working_dir.exists() and any(working_dir.iterdir()):
        logger.error("Directory should be empty !")
        raise typer.Abort()
    ctx.setup(version=__version__, working_dir=working_dir)


@cli.command(short_help="Drop OdooGhost environment")
def drop() -> None:
    """
    Drop OdooGhost environment and all it's related data
    """
    raise NotImplementedError()


@cli.command()
def web() -> None:
    """
    Run OdooGhost webserver
    """
    raise NotImplementedError()


@cli.callback()
def callback() -> None:
    """
    OdooGhost make Odoo development easy
    """
