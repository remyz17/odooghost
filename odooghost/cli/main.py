import typer

cli = typer.Typer(no_args_is_help=True)


@cli.callback()
def callback() -> None:
    """
    OdooGhost make Odoo development easy
    """
