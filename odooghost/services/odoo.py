from odooghost import stack

from .base import BaseService


class OdooService(BaseService):
    def __init__(self, config: stack.OdooStackConfig) -> None:
        self._config = config
        super().__init__()

    def build_image(self) -> None:
        super().build_image()

    @property
    def image_tag(self) -> str:
        return f"odoo:{self._config.version}"

    @property
    def has_custom_image(self) -> bool:
        return True
