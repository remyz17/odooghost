from odooghost import stack

from .base import BaseService


class PostgresService(BaseService):
    def __init__(self, config: stack.PostgresStackConfig) -> None:
        self._config = config
        super().__init__()

    def build_image(self) -> None:
        return super().build_image()

    @property
    def is_remote(self) -> bool:
        return self._config.type == "remote"

    @property
    def image_tag(self) -> str:
        return f"postgres:{self._config.version}"

    @property
    def has_custom_image(self) -> bool:
        return False
