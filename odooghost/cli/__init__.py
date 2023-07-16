from odooghost import logger
from odooghost.cli.root import cli


def main() -> None:
    logger.setup_cli_logging()
    cli()
