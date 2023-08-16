import typer

from odooghost.context import ctx

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def version() -> None:
    """
    Print config version
    """
    print(ctx.config.version)


@cli.command()
def working_dir() -> None:
    """
    Print working directory
    """
    print(ctx.config.working_dir.as_posix())


@cli.callback()
def callback() -> None:
    """
    Config subcommands allow you to manage OdooGhost config
    """
