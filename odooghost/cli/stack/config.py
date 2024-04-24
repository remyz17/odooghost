import typing as t
from pathlib import Path

import typer
from loguru import logger
from pydantic import ValidationError

from odooghost.stack import Stack
from odooghost.utils.autocomplete import ac_stack_configs

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
            autocompletion=ac_stack_configs,
        ),
    ]
) -> None:
    """
    Check stack config
    """
    for config in configs:
        try:
            Stack.from_file(file_path=config)
        except ValidationError as exc:
            logger.error(
                f"Stack config validation failed for file {config.name}:\n {exc}\n"
            )
        else:
            logger.success(f"Successfully validated file {config.name}")
