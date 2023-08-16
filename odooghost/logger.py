import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    """
    InterceptHandler convert default logging LogRecord to loguru format
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_cli_logging() -> None:
    """
    Setup logger for CLI
    """
    logger.configure(
        handlers=[
            dict(
                sink=sys.stderr,
                backtrace=True,
                diagnose=True,
                level="DEBUG",
                format="<level>{message}</level>",
            )
        ]
    )
