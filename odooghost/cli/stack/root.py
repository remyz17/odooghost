import sys
import typing as t
import webbrowser
from pathlib import Path

import typer
from loguru import logger

from odooghost import constant, exceptions
from odooghost.stack import Stack
from odooghost.utils import signals
from odooghost.utils.autocomplete import (
    ac_stack_configs,
    ac_stacks_lists,
    ac_stacks_services,
)

from .config import cli as configCLI
from .data import cli as dataCLI

if not constant.IS_WINDOWS_PLATFORM:
    from dockerpty.pty import PseudoTerminal, RunOperation


cli = typer.Typer(no_args_is_help=True)
cli.add_typer(configCLI, name="config", help="Manage Stack config")
cli.add_typer(dataCLI, name="data", help="Manage Stack data")


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
            raise typer.Exit(code=1)


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
            raise typer.Exit(code=1)


@cli.command()
def pull(
    stack_names: t.Annotated[
        t.List[str],
        typer.Argument(..., help="Stack names"),
    ],
) -> None:
    """
    Pull stack(s) images and service(s) related data
    """
    for name in stack_names:
        try:
            Stack.from_name(name=name).pull()
        except exceptions.StackException as err:
            logger.error(err)
            raise typer.Exit(code=1)


@cli.command()
def update(
    stack_configs: t.Annotated[
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
    ],
    do_pull: t.Annotated[
        bool, typer.Option("--no-pull", help="Pull stack service")
    ] = True,
) -> None:
    """
    Pull stack(s) images and service(s) related data
    """
    for config in stack_configs:
        try:
            Stack.from_file(file_path=config).update(do_pull=do_pull)
        except exceptions.StackException as err:
            logger.error(err)
            raise typer.Exit(code=1)


@cli.command()
def start(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name", autocompletion=ac_stacks_lists),
    ],
    detach: t.Annotated[
        bool, typer.Option("--detach", help="Do not stream Odoo service logs")
    ] = False,
    open: t.Annotated[bool, typer.Option("--open", help="Open in browser")] = False,
    open_mode: t.Annotated[
        constant.OpenMode, typer.Option("--open-mode", help="Open mode")
    ] = (
        constant.OpenMode.subnet
        if constant.IS_LINUX_PLATFORM
        else constant.OpenMode.local
    ),
    tail: t.Annotated[
        int,
        typer.Option("--tail", help="Number of lines to show from the end of the logs"),
    ] = 1,
) -> None:
    """
    Start stack
    """
    try:
        stack = Stack.from_name(name=stack_name)
        stack.start()
        odoo = stack.get_service(name="odoo").get_container()
        if open:
            webbrowser.open(
                f"http://{odoo.get_subnet_port(8069) if open_mode == constant.OpenMode.subnet else odoo.get_local_port(8069)}"
            )
        if not detach:
            while True:
                try:
                    odoo.stream_logs(tail=tail)
                except KeyboardInterrupt:
                    logger.info("Stopping Stack ...")
                    stack.stop()
                    break
    except exceptions.StackException as err:
        logger.error(f"Failed to start stack {stack_name}: {err}")
        raise typer.Exit(code=1)


@cli.command()
def stop(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name", autocompletion=ac_stacks_lists),
    ],
    timeout: t.Annotated[
        int, typer.Option(help="Stop timeout before sending SIGKILL")
    ] = 10,
    wait: t.Annotated[
        bool, typer.Option("--wait", help="Wait for the stack to stop")
    ] = False,
) -> None:
    """
    Stop stack
    """
    try:
        Stack.from_name(name=stack_name).stop(timeout=timeout, wait=wait)
    except exceptions.StackException as err:
        logger.error(f"Failed to stop stack {stack_name}: {err}")
        raise typer.Exit(code=1)


@cli.command()
def restart(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name", autocompletion=ac_stacks_lists),
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
        raise typer.Exit(code=1)


@cli.command()
def logs(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name", autocompletion=ac_stacks_lists),
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
    Print stack logs
    """
    try:
        stack = Stack.from_name(name=stack_name)
        odoo = stack.get_service(name="odoo").get_container()
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
        raise typer.Exit(code=1)


@cli.command()
def exec(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name", autocompletion=ac_stacks_lists),
    ],
    service_name: t.Annotated[
        str,
        typer.Argument(..., help="Service name", autocompletion=ac_stacks_services),
    ],
    command: t.Annotated[
        str,
        typer.Argument(..., help="Command"),
    ],
    command_args: t.Annotated[
        t.Optional[t.List[str]],
        typer.Argument(..., help="Args"),
    ] = None,
    detach: t.Annotated[
        bool, typer.Option("-d", "--detach", help="Run command in the background")
    ] = False,
    privileged: t.Annotated[
        bool,
        typer.Option("--privileged", help="Give extended privileges to the process"),
    ] = False,
    user: t.Annotated[
        t.Optional[str],
        typer.Option("-u", "--user", help="Run the command as this user"),
    ] = None,
    tty: t.Annotated[
        bool, typer.Option("--no-tty", help="Disable pseudo-tty allocation.")
    ] = True,
    workdir: t.Annotated[
        t.Optional[str],
        typer.Option(
            "-w", "--workdir", help="Path to workdir directory for this command"
        ),
    ] = None,
) -> None:
    """
    Execute a command in a running container
    """
    ...
    try:
        stack = Stack.from_name(name=stack_name)
        service = stack.get_service(name=service_name)
        container = service.get_container()

        command = [command] + command_args
        exit_code, res = container.exec_run(
            command=command,
            stdin=not detach,
            detach=detach,
            privileged=privileged,
            user=user,
            tty=tty,
            stream=True,
            workdir=workdir,
            pseudo_tty=True,
        )
        logger.info(f"Exec command exited with code: {exit_code} and res: {res}")
    except exceptions.StackException as err:
        logger.error(f"Failed to exec command in stack {stack_name}: {err}")
        raise typer.Exit(code=1)


@cli.command()
def run(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name", autocompletion=ac_stacks_lists),
    ],
    service_name: t.Annotated[
        str,
        typer.Argument(..., help="Service name", autocompletion=ac_stacks_services),
    ],
    command: t.Annotated[
        str,
        typer.Argument(..., help="Command"),
    ],
    command_args: t.Annotated[
        t.Optional[t.List[str]],
        typer.Argument(..., help="Args"),
    ] = None,
    detach: t.Annotated[
        bool, typer.Option("-d", "--detach", help="Run command in the background")
    ] = False,
    user: t.Annotated[
        t.Optional[str],
        typer.Option("-u", "--user", help="Run the command as this user"),
    ] = None,
    tty: t.Annotated[
        bool, typer.Option("--no-tty", help="Disable pseudo-tty allocation.")
    ] = True,
    workdir: t.Annotated[
        t.Optional[str],
        typer.Option(
            "-w", "--workdir", help="Path to workdir directory for this command"
        ),
    ] = None,
    port: t.Annotated[
        bool,
        typer.Option("-p", "--port", help="Bind service port"),
    ] = False,
) -> None:
    """
    Run a one-off command on a service
    """
    try:
        stack = Stack.from_name(name=stack_name)
        one_off_service = stack.get_service(name=service_name)
        service_deps = [
            service
            for service in stack.services()
            if service.name != one_off_service.name
        ]
        for service in service_deps:
            service.start_container()

        override_options = {
            "command": [command] + command_args,
            "tty": not (detach or not tty or not sys.stdin.isatty()),
            "stdin_open": True,
            "detach": detach,
            "auto_remove": True,
        }
        if port:
            # looks like ruff want to make this a tuple instead of a dict when putting directly in dict
            ports = {"8069/tcp": one_off_service.config.service_port}
            override_options["ports"] = ports

        if user is not None:
            override_options["user"] = user

        if workdir is not None:
            override_options["workdir"] = workdir

        container = one_off_service.create_container(one_off=True, **override_options)

        if detach:
            container.start()
            logger.info(f"Started one off container: {container.name}")
            return

        signals.set_signal_handler_to_shutdown()
        signals.set_signal_handler_to_hang_up()
        try:
            try:
                operation = RunOperation(
                    container.client,
                    container.id,
                    interactive=tty,
                    logs=False,
                )
                pty = PseudoTerminal(container.client, operation)
                sockets = pty.sockets()
                container.start()
                pty.start(sockets)
                exit_code = container.wait()
            except signals.ShutdownException:
                container.stop()
                exit_code = 1
        except (signals.ShutdownException, signals.HangUpException):
            container.kill()
            exit_code = 2

        logger.info(f"Exec command exited with code: {exit_code}")

    except exceptions.StackException as err:
        logger.error(f"Failed to exec command in stack {stack_name}: {err}")
        raise typer.Exit(code=1)


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
