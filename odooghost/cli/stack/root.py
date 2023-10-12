import typing as t
import webbrowser
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
    ],
    force_recreate: t.Annotated[
        bool,
        typer.Option(
            "--force-recreate",
            help="Force container recreate when dangling container already exists",
        ),
    ] = False,
    do_pull: t.Annotated[
        bool,
        typer.Option(
            "--no-pull",
            help="Do not pull base images",
        ),
    ] = True,
) -> None:
    """
    Create one or more stack
    """
    for config in stack_configs:
        try:
            Stack.from_file(file_path=config).create(
                force=force_recreate, do_pull=do_pull
            )
        except exceptions.StackException as err:
            logger.error(f"Failed to create stack from config {config.name}: {err}")


@cli.command()
def drop(
    stack_names: t.Annotated[
        t.List[str],
        typer.Argument(..., help="Stack names"),
    ],
    volumes: t.Annotated[
        bool,
        typer.Option(
            "--volumes",
            help="Drop services volumes",
        ),
    ] = False,
) -> None:
    """
    Drop stack(s) and related data
    """
    for name in stack_names:
        try:
            Stack.from_name(name=name).drop(volumes=volumes)
        except exceptions.StackException as err:
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
    ],
    detach: t.Annotated[
        bool, typer.Option("--detach", help="Do not stream Odoo service logs")
    ] = False,
    open: t.Annotated[bool, typer.Option("--open", help="Open in browser")] = False,
) -> None:
    """
    Start stack
    """
    try:
        stack = Stack.from_name(name=stack_name)
        stack.start()
        odoo = stack.odoo_service.get_container()
        if open:
            webbrowser.open(f"http://{odoo.get_subnet_ip()}:8069")
        if not detach:
            while True:
                try:
                    odoo.stream_logs()
                except KeyboardInterrupt:
                    logger.info("Stopping Stack ...")
                    odoo.stop()
                    stack.postgres_service.get_container().stop()
                    break
    except exceptions.StackException as err:
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
    wait: t.Annotated[bool, typer.Option("--open", help="Open in browser")] = False,
) -> None:
    """
    Stop stack
    """
    try:
        Stack.from_name(name=stack_name).stop(timeout=timeout, wait=wait)
    except exceptions.StackException as err:
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
    except exceptions.StackException as err:
        logger.error(f"Failed to start stack {stack_name}: {err}")


@cli.command()
def logs(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name"),
    ],
    follow: t.Annotated[
        bool, typer.Option("--follow", help="Follow logs stream")
    ] = False,
    tail: t.Annotated[
        int,
        typer.Option("--tail", help="Number of lines to show from the end of the logs"),
    ] = 0,
) -> None:
    """
    Start stack
    """
    try:
        stack = Stack.from_name(name=stack_name)
        odoo = stack.odoo_service.get_container()
        tail = "all" if tail == 0 else tail
        if not follow or not odoo.is_running:
            if follow:
                logger.warning("Container not running, can not follow logs")
            odoo.stream_logs(follow=False, tail=tail)
        else:
            while True:
                try:
                    odoo.stream_logs(tail=tail)
                except KeyboardInterrupt:
                    break
    except exceptions.StackException as err:
        logger.error(f"Failed to stream stack {stack_name} logs: {err}")


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
    for stack in Stack.list(running=True):
        logger.info(stack.name)


@cli.callback()
def callback() -> None:
    """
    Stack subcommands allow you to manage Odoo stacks
    """
