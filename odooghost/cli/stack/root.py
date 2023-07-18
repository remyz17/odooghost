import typing as t
from pathlib import Path

import typer
from loguru import logger
from pydantic import ValidationError

from odooghost import stack

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def check(
    configs: t.Annotated[
        t.List[Path],
        typer.Argument(
            ...,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            exists=True,
        ),
    ]
) -> None:
    """
    Check stack config
    """
    for config in configs:
        try:
            stack.Stack.from_file(file_path=config)
        except ValidationError as exc:
            logger.error(
                f"Stack config validation failed for file {config.name}:\n {exc}\n"
            )
        else:
            logger.success(f"Successfully validated file {config.name}")


@cli.command()
def create() -> None:
    """
    Create one or more stack
    """


@cli.command()
def drop() -> None:
    """
    Drop stack and it's related data
    """


@cli.command()
def update() -> None:
    """
    Update stack
    """


@cli.command()
def start() -> None:
    """
    Start stack
    """


@cli.command()
def stop() -> None:
    """
    Stop stack
    """


@cli.command()
def restart() -> None:
    """
    Restart stack
    """


@cli.command()
def ls() -> None:
    """
    List created stacks
    """


@cli.command()
def ps() -> None:
    """
    List running stacks
    """


@cli.callback()
def callback() -> None:
    """
    Stack subcommands allow you to manage Odoo stacks
    """
