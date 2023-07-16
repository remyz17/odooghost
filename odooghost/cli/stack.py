import typer

cli = typer.Typer(no_args_is_help=True)


@cli.callback()
def callback() -> None:
    """
    Stack subcommands allow you to manage Odoo stacks
    """
