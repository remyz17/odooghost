import typing as t
from pathlib import Path

import typer
from loguru import logger
from pydantic import ValidationError

from odooghost import exceptions, stack

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
def create(
    stack_configs: t.Annotated[
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
    Create one or more stack
    """
    for config in stack_configs:
        try:
            stack.Stack.from_file(file_path=config).create()
        except (
            exceptions.StackAlreadyExistsError,
            exceptions.StackImageEnsureError,
            exceptions.StackImageBuildError,
        ) as err:
            logger.error(f"Failed to create stack from config {config.name}: {err}")


@cli.command()
def drop(
    stack_configs: t.Annotated[
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
    Drop stack(s) and related data
    """
    for config in stack_configs:
        try:
            stack.Stack.from_file(file_path=config).drop()
        except (exceptions.StackNotFoundError,) as err:
            logger.error(f"Failed to drop stack from config {config.name}: {err}")


@cli.command()
def update() -> None:
    """
    Update stack
    """
    raise NotImplementedError()


@cli.command()
def start(
    stack_config: t.Annotated[
        Path,
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
    Start stack
    """
    try:
        stack.Stack.from_file(file_path=stack_config).start()
    except (exceptions.StackNotFoundError,) as err:
        logger.error(f"Failed to start stack {stack_config.name}: {err}")


@cli.command()
def stop(
    stack_config: t.Annotated[
        Path,
        typer.Argument(
            ...,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            exists=True,
        ),
    ],
    timeout: t.Annotated[
        int, typer.Option(help="Stop timeout before sending SIGKILL")
    ] = 10,
) -> None:
    """
    Stop stack
    """
    try:
        stack.Stack.from_file(file_path=stack_config).stop(timeout=timeout)
    except (exceptions.StackNotFoundError,) as err:
        logger.error(f"Failed to start stack {stack_config.name}: {err}")


@cli.command()
def restart(
    stack_config: t.Annotated[
        Path,
        typer.Argument(
            ...,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            exists=True,
        ),
    ],
    timeout: t.Annotated[
        int, typer.Option(help="Stop timeout before sending SIGKILL")
    ] = 10,
) -> None:
    """
    Restart stack
    """
    try:
        stack.Stack.from_file(file_path=stack_config).restart(timeout=timeout)
    except (exceptions.StackNotFoundError,) as err:
        logger.error(f"Failed to start stack {stack_config.name}: {err}")


@cli.command()
def ls() -> None:
    """
    List created stacks
    """
    raise NotImplementedError()


@cli.command()
def ps() -> None:
    """
    List running stacks
    """
    raise NotImplementedError()


@cli.callback()
def callback() -> None:
    """
    Stack subcommands allow you to manage Odoo stacks
    """
