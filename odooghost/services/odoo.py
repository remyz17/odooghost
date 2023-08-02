from odooghost import stack

from .base import BaseService


class OdooService(BaseService):
    def __init__(self, config: stack.OdooStackConfig) -> None:
        self._config = config
        super().__init__()

    @property
    def image_tag(self) -> str:
        return f"odoo:{self._config.version}"
