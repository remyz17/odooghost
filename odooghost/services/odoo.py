import typing as t

from .base import BaseService

if t.TYPE_CHECKING:
    from odooghost import config


class OdooService(BaseService):
    def __init__(self, config: "config.OdooStackConfig") -> None:
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
