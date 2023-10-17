import typing as t
from pathlib import Path

import typer

from odooghost import exceptions
from odooghost.stack import Stack

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def restore(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name"),
    ],
    db_name: t.Annotated[str, typer.Argument(help="Database name")],
    dump_path: t.Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=True,
            readable=True,
            resolve_path=True,
            exists=True,
            help="Database dump path",
        ),
    ],
    filestore_path: t.Annotated[
        t.Optional[Path],
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            exists=True,
            help="Database dump path",
        ),
    ] = None,
) -> None:
    """
    Restore
    """
    try:
        stack = Stack.from_name(name=stack_name)
        db_service = stack.get_service(name="db")
        c = db_service.get_container()
        res = c.exec_run(command=["psql", "-l", "-U", "odoo"])
        print(res)
    except exceptions.StackException:
        pass


@cli.callback()
def callback() -> None:
    """
    Data subcommands allow you to manage Odoo stacks data
    """
