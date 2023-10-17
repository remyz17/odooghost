import typing as t
from pathlib import Path

import typer

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
    print(dump_path, filestore_path)


@cli.callback()
def callback() -> None:
    """
    Data subcommands allow you to manage Odoo stacks data
    """
