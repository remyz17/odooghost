import typing as t

from .base import BaseService

if t.TYPE_CHECKING:
    from odooghost import config


class MailService(BaseService):
    name = "mail"

    def __init__(self, stack_config: "config.StackConfig") -> None:
        super().__init__(stack_config=stack_config)

    def _get_container_options(self, one_off: bool = False) -> t.Dict[str, t.Any]:
        return super()._get_container_options(one_off)

    def _get_environment(self) -> t.Dict[str, t.Any]:
        return super()._get_environment()

    @property
    def config(self) -> "config.MailStackConfig":
        return super().config

    @property
    def base_image_tag(self) -> str:
        return f"mailhog/mailhog:{self.config.version}"

    @property
    def has_custom_image(self) -> bool:
        return False

    @property
    def container_port(self) -> int:
        return 8025
