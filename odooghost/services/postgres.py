import typing as t

from docker.types import Mount
from loguru import logger

from odooghost import constant
from odooghost.container import Container

from .base import BaseService

if t.TYPE_CHECKING:
    from odooghost import config


class PostgresService(BaseService):
    def __init__(self, stack_name: str, config: "config.PostgresStackConfig") -> None:
        self._config = config
        super().__init__(name="db", stack_name=stack_name)

    def ensure_base_image(self, do_pull: bool = False) -> None:
        if self._config.type == "remote":
            logger.warning("Skip postgres image as it's remote type")
        return super().ensure_base_image(do_pull)

    def create_container(self) -> Container:
        return super().create_container(
            name=self.container_name,
            image=self.base_image_tag,
            hostname="db",
            labels=self.labels(),
            environment={
                "POSTGRES_DB": "postgres",
                "POSTGRES_PASSWORD": "odoo",
                "POSTGRES_USER": "odoo",
            },
            mounts=[
                Mount(
                    source=self.volume_name,
                    target="/var/lib/postgresql/data",
                    type="volume",
                )
            ],
            network=constant.COMMON_NETWORK_NAME,
        )

    @property
    def is_remote(self) -> bool:
        return self._config.type == "remote"

    @property
    def base_image_tag(self) -> str:
        return f"postgres:{self._config.version}"

    @property
    def has_custom_image(self) -> bool:
        return False
