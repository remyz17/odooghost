import typer

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def version() -> None:
    """
    Print config version
    """
    raise NotImplementedError()


@cli.command()
def working_dir() -> None:
    """
    Print working directory
    """
    raise NotImplementedError()


@cli.callback()
def callback() -> None:
    """
    Config subcommands allow you to manage OdooGhost config
    """
