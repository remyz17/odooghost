import enum
import typing as t
from pathlib import Path

from loguru import logger

from odooghost import config, constant, services
from odooghost.container import Container
from odooghost.context import ctx
from odooghost.exceptions import StackAlreadyExistsError, StackNotFoundError
from odooghost.types import Filters, Labels
from odooghost.utils.docker import labels_as_list, stream_container_logs


class StackState(enum.Enum):
    NONE: int = 0
    PARTIAL: int = 1
    READY: int = 2


class Stack:
    """
    Stack manage differents Odoo stacks regarding it's config
    """

    def __init__(self, config: "config.StackConfig") -> None:
        self._config = config
        # TODO handle better
        self._config_file = ctx.get_stack_config_path(self.name)
        self._postgres_service = None
        self._odoo_service = None

    def _check_state(self) -> StackState:
        if not self._config_file.exists():
            return StackState.NONE
        # TODO implement partial state
        return StackState.READY

    @classmethod
    def from_file(cls, file_path: Path) -> "Stack":
        return cls(config=config.StackConfig.from_file(file_path=file_path))

    @classmethod
    def from_name(cls, name: str) -> "Stack":
        return cls.from_file(ctx.get_stack_config_path(name))

    @classmethod
    def list(cls, running: bool = False) -> t.Generator:
        """
        List all stacks
        """
        # TODO implment running stack only
        for config_file_path in ctx._stack_dir.iterdir():
            if running:
                raise NotImplementedError()
            yield cls(config=config.StackConfig.from_file(file_path=config_file_path))

    def save_config(self) -> None:
        # maybe put in context
        ...

    def reload_config(self) -> None:
        # maybe put in context
        ...

    def labels(self) -> Labels:
        return {
            constant.LABEL_NAME: "true",
            constant.LABEL_STACKNAME: self.name,
        }

    def containers(
        self,
        filters: t.Optional[Filters] = None,
        labels: t.Optional[Labels] = None,
        stopped: bool = False,
    ) -> t.List[Container]:
        if filters is None:
            filters = {}
        filters.update(
            {
                "label": labels_as_list(self.labels())
                + (labels_as_list(labels) if labels else [])
            }
        )
        return list(
            filter(
                None,
                [
                    Container.from_ps(container)
                    for container in ctx.docker.api.containers(
                        all=stopped, filters=filters
                    )
                ],
            )
        )

    def ensure_addons(self) -> None:
        pass

    def create(self, do_pull: bool = False, ensure_addons: bool = False) -> None:
        logger.info(f"Creating Stack {self.name} ...")
        if self.exists:
            raise StackAlreadyExistsError(f"Stack {self.name} already exists !")
        if ensure_addons:
            self.ensure_addons()
        # TODO allow custom network
        ctx.ensure_common_network()
        self.postgres_service.create(do_pull=do_pull)
        self.odoo_service.create(do_pull=do_pull)
        logger.info(f"Created Stack {self.name} !")

    def drop(self, volumes: bool = False) -> None:
        logger.info(f"Dropping Stack {self.name} ...")
        if not self.exists:
            raise StackNotFoundError(f"Stack {self.name} does not exists !")
        self.odoo_service.drop(volumes=volumes)
        self.postgres_service.drop(volumes=volumes)
        logger.info(f"Dropped Stack {self.name} !")

    def update(self) -> None:
        raise NotImplementedError()

    def start(self, detach: bool = False, open_browser: bool = False) -> None:
        if not self.exists:
            raise StackNotFoundError(f"Stack {self.name} does not exists !")
        db_container = self.postgres_service.start_container()
        odoo_container = self.odoo_service.start_container()
        if open_browser:
            pass
        if not detach:
            while True:
                try:
                    stream_container_logs(odoo_container)
                except KeyboardInterrupt:
                    logger.info("Interrupt, stopping containers ...")
                    odoo_container.stop()
                    db_container.stop()
                    break

    def stop(self, timeout: int = 10) -> None:
        if not self.exists:
            raise StackNotFoundError(f"Stack {self.name} does not exists !")
        containers = self.containers(stopped=False)
        if not len(containers):
            logger.warning("No container to stop !")
            return
        for container in containers:
            logger.info(f"Stopping container {container.name}")
            container.stop(timeout=timeout)

    def restart(self, timeout: int = 10) -> None:
        if not self.exists:
            raise StackNotFoundError(f"Stack {self.name} does not exists !")
        containers = self.containers(stopped=False)
        if not len(containers):
            logger.warning("No container to restart !")
            return
        for container in containers:
            logger.info(f"Restarting container {container.name}")
            container.restart(timeout=timeout)

    @property
    def name(self) -> str:
        """
        Return name of stack

        Returns:
            str: Stack name
        """
        return self._config.name

    @property
    def state(self) -> StackState:
        return self._check_state()

    @property
    def odoo_service(self) -> "services.odoo.OdooService":
        """
        Lazy OdooService getter

        Returns:
            services.odoo.OdooService: OdooService instance
        """
        if not self._odoo_service:
            self._odoo_service = services.odoo.OdooService(
                stack_name=self.name, config=self._config.odoo
            )
        return self._odoo_service

    @property
    def postgres_service(self) -> "services.postgres.PostgresService":
        """
        Lazy PostgresService getter

        Returns:
            services.postgres.PostgresService: PostgresService instance
        """
        if not self._postgres_service:
            self._postgres_service = services.postgres.PostgresService(
                stack_name=self.name, config=self._config.postgres
            )
        return self._postgres_service

    @property
    def exists(self) -> bool:
        """
        Check if stack already exists

        Returns:
            bool
        """
        return self.state != StackState.NONE
