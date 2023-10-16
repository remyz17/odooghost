import sys
import typing as t
import webbrowser
from pathlib import Path

import typer
from loguru import logger
from pydantic import ValidationError

from odooghost import constant, exceptions
from odooghost.stack import Stack
from odooghost.utils import signals

if not constant.IS_WINDOWS_PLATFORM:
    from dockerpty.pty import ExecOperation, PseudoTerminal, RunOperation


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
        odoo = stack.get_service(name="odoo").get_container()
        if open:
            webbrowser.open(f"http://{odoo.get_subnet_ip()}:8069")
        if not detach:
            while True:
                try:
                    odoo.stream_logs()
                except KeyboardInterrupt:
                    logger.info("Stopping Stack ...")
                    stack.stop()
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


@cli.command()
def exec(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name"),
    ],
    service_name: t.Annotated[
        str,
        typer.Argument(..., help="Service name"),
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
        exec_id = container.create_exec(
            command,
            privileged=privileged,
            user=user,
            tty=tty,
            stdin=True,
            workdir=workdir,
        )

        if detach:
            container.start_exec(exec_id, tty=tty, stream=True)
            return

        signals.set_signal_handler_to_shutdown()
        try:
            operation = ExecOperation(
                container.client,
                exec_id,
                interactive=tty,
            )
            pty = PseudoTerminal(container.client, operation)
            pty.start()
        except signals.ShutdownException:
            logger.info("received shutdown exception: closing")
        exit_code = container.client.exec_inspect(exec_id).get("ExitCode")
        logger.info(f"Exec command exited with code: {exit_code}")
    except exceptions.StackException as err:
        logger.error(f"Failed to exec command in stack {stack_name}: {err}")


@cli.command()
def run(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name"),
    ],
    service_name: t.Annotated[
        str,
        typer.Argument(..., help="Service name"),
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
