import typing as t
from pathlib import Path

import typer
from loguru import logger
from pydantic import ValidationError

from odooghost import exceptions
from odooghost.stack import Stack

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
            Stack.from_file(file_path=config)
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
            Stack.from_file(file_path=config).create()
        except (
            exceptions.StackAlreadyExistsError,
            exceptions.StackImageEnsureError,
            exceptions.StackImageBuildError,
        ) as err:
            logger.error(f"Failed to create stack from config {config.name}: {err}")


@cli.command()
def drop(
    stack_names: t.Annotated[
        t.List[str],
        typer.Argument(..., help="Stack names"),
    ]
) -> None:
    """
    Drop stack(s) and related data
    """
    for name in stack_names:
        try:
            Stack.from_name(name=name).drop()
        except (exceptions.StackNotFoundError,) as err:
            logger.error(err)


@cli.command()
def update() -> None:
    """
    Update stack
    """
    raise NotImplementedError()


@cli.command()
def start(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name"),
    ]
) -> None:
    """
    Start stack
    """
    try:
        stack = Stack.from_name(name=stack_name)
        stack.start()
    except (exceptions.StackNotFoundError,) as err:
        logger.error(f"Failed to start stack {stack_name}: {err}")


@cli.command()
def stop(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name"),
    ],
    timeout: t.Annotated[
        int, typer.Option(help="Stop timeout before sending SIGKILL")
    ] = 10,
) -> None:
    """
    Stop stack
    """
    try:
        Stack.from_name(name=stack_name).stop(timeout=timeout)
    except (exceptions.StackNotFoundError,) as err:
        logger.error(f"Failed to start stack {stack_name}: {err}")


@cli.command()
def restart(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name"),
    ],
    timeout: t.Annotated[
        int, typer.Option(help="Stop timeout before sending SIGKILL")
    ] = 10,
) -> None:
    """
    Restart stack
    """
    try:
        Stack.from_name(name=stack_name).restart(timeout=timeout)
    except (exceptions.StackNotFoundError,) as err:
        logger.error(f"Failed to start stack {stack_name}: {err}")


@cli.command()
def ls() -> None:
    """
    List created stacks
    """
    for stack in Stack.list():
        logger.info(stack.name)


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
