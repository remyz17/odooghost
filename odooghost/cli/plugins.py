import typer

from odooghost.utils import plugins
from loguru import logger

cli = typer.Typer(no_args_is_help=True)

plugins_list = plugins.Plugins()


@cli.command("list")
@cli.command("ls", hidden=True)
def list() -> None:
    """
    List installed plugins. (Alias: ls)
    """
    if not plugins_list.plugins:
        logger.info("No plugins installed")
        return
    logger.info(f"There are {len(plugins_list.plugins)} installed plugins:")
    for name, plugin in plugins_list.plugins:
        logger.info(f"- {name} | {plugin.__version__}")
        
@cli.callback()
def callback() -> None:
    """
    Plugin subcommands allow you to manage OdooGhost plugins
    """
