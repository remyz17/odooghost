import typing as t

from docker.errors import APIError
from docker.types import Mount
from loguru import logger

from odooghost import constant, exceptions
from odooghost.context import ctx

from .base import BaseService

if t.TYPE_CHECKING:
    from odooghost import config


class PostgresService(BaseService):
    def __init__(self, stack_name: str, config: "config.PostgresStackConfig") -> None:
        self._config = config
        super().__init__(name="db", stack_name=stack_name)

    def _get_container_labels(self) -> dict[str, str]:
        return super()._get_container_labels()

    def ensure_base_image(self, do_pull: bool = False) -> None:
        if self._config.type == "remote":
            logger.debug("Skip postgres image as it's remote type")
        return super().ensure_base_image(do_pull)

    def build_image(self, rm: bool = True, no_cache: bool = False) -> None:
        return super().build_image(rm=rm, no_cache=no_cache)

    def create_volumes(self) -> None:
        return super().create_volumes()

    def create_container(self) -> None:
        try:
            ctx.docker.containers.create(
                name=self.container_name,
                image=self.base_image_tag,
                hostname="db",
                labels=self._get_container_labels(),
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
        except APIError as err:
            raise exceptions.StackContainerCreateError(
                f"Failed to create db container: {err}"
            )

    def create(self, do_pull: bool) -> None:
        return super().create(do_pull=do_pull)

    @property
    def is_remote(self) -> bool:
        return self._config.type == "remote"

    @property
    def base_image_tag(self) -> str:
        return f"postgres:{self._config.version}"

    @property
    def has_custom_image(self) -> bool:
        return False
