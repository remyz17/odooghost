import typing as t

from loguru import logger

from .base import BaseService

if t.TYPE_CHECKING:
    from odooghost import config


class PostgresService(BaseService):
    def __init__(self, stack_name: str, config: "config.PostgresStackConfig") -> None:
        self.stack_name = stack_name
        self._config = config
        super().__init__()

    def ensure_base_image(self, do_pull: bool = False) -> None:
        if self._config.type == "remote":
            logger.debug("Skip postgres image as it's remote type")
        return super().ensure_base_image(do_pull)

    def build_image(self) -> None:
        return super().build_image()

    @property
    def is_remote(self) -> bool:
        return self._config.type == "remote"

    @property
    def base_image_tag(self) -> str:
        return f"postgres:{self._config.version}"

    @property
    def has_custom_image(self) -> bool:
        return False
