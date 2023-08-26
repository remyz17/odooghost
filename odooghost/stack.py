import enum
import typing as t
from pathlib import Path

from loguru import logger

from odooghost import config, constant, services
from odooghost.container import Container
from odooghost.context import ctx
from odooghost.exceptions import StackAlreadyExistsError, StackNotFoundError
from odooghost.types import Filters, Labels
from odooghost.utils.misc import labels_as_list


class StackState(enum.Enum):
    """
    StackState obviously holds StackState
    """

    NONE: int = 0
    PARTIAL: int = 1
    READY: int = 2


class Stack:
    """
    Stack manage differents Odoo stacks regarding it's config
    """

    def __init__(self, config: "config.StackConfig") -> None:
        self._config = config
        self._postgres_service = None
        self._odoo_service = None

    def _check_state(self) -> StackState:
        """
        Check Stack state

        Returns:
            StackState: return current state
        """
        if self.name not in ctx.stacks:
            return StackState.NONE
        # TODO implement partial state
        return StackState.READY

    @classmethod
    def from_file(cls, file_path: Path) -> "Stack":
        """
        Instanciate Stack from file

        File could be both YAML and JSON

        Args:
            file_path (Path): stack config file path

        Returns:
            Stack: Stack instance
        """
        return cls(config=config.StackConfig.from_file(file_path=file_path))

    @classmethod
    def from_name(cls, name: str) -> "Stack":
        """
        Instanciate Stack from name
        Stack config will be searched from Context

        Args:
            name (str): Stack name

        Returns:
            Stack: Stack instance
        """
        return cls(config=ctx.stacks.get(stack_name=name))

    @classmethod
    def list(cls, running: bool = False) -> t.Generator["Stack", None, None]:
        """
        List all stacks

        Yields:
            Srack: Stack instance
        """
        # TODO implment running stack only
        for stack_config in ctx.stacks:
            if running:
                raise NotImplementedError()
            yield cls(config=stack_config)

    def labels(self) -> Labels:
        """
        Get Stack labels

        Returns:
            Labels: Labels as dict
        """
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
        """
        Get Stack containers

        Args:
            filters (t.Optional[Filters], optional): Search filters. Defaults to None.
            labels (t.Optional[Labels], optional): Additionnal search labels. Defaults to None.
            stopped (bool, optional): Get stopped containers. Defaults to False.

        Returns:
            t.List[Container]: Container list
        """
        if filters is None:
            filters = {}
        filters.update(
            {
                "label": labels_as_list(self.labels())
                + (labels_as_list(labels) if labels else [])
            }
        )
        return Container.search(filters=filters, stopped=stopped)

    def ensure_addons(self) -> None:
        pass

    def create(self, do_pull: bool = False, ensure_addons: bool = False) -> None:
        """
        Create Stack

        Args:
            do_pull (bool, optional): Pull base images. Defaults to False.
            ensure_addons (bool, optional): Ensure Odoo addons. Defaults to False.

        Raises:
            StackAlreadyExistsError: When Stack alreary exists
        """
        if self.exists:
            raise StackAlreadyExistsError(f"Stack {self.name} already exists !")
        logger.info(f"Creating Stack {self.name} ...")
        if ensure_addons:
            self.ensure_addons()
        # TODO allow custom network
        ctx.ensure_common_network()
        self.postgres_service.create(do_pull=do_pull)
        self.odoo_service.create(do_pull=do_pull)
        logger.info("Saving Stack config ...")
        ctx.stacks.create(config=self._config)
        logger.info(f"Created Stack {self.name} !")

    def drop(self, volumes: bool = False) -> None:
        """
        Drop Stack

        Args:
            volumes (bool, optional): Drop volumes. Defaults to False.

        Raises:
            StackNotFoundError: When Stack does not exists
        """
        if not self.exists:
            raise StackNotFoundError(f"Stack {self.name} does not exists !")
        logger.info(f"Dropping Stack {self.name} ...")
        self.odoo_service.drop(volumes=volumes)
        self.postgres_service.drop(volumes=volumes)
        logger.info("Dropping Stack config ...")
        ctx.stacks.drop(stack_name=self.name)
        logger.info(f"Dropped Stack {self.name} !")

    def update(self) -> None:
        raise NotImplementedError()

    def start(self) -> None:
        """
        Start Stack

        Raises:
            StackNotFoundError: When Stack does not exists
        """
        if not self.exists:
            raise StackNotFoundError(f"Stack {self.name} does not exists !")
        containers = self.containers(stopped=True)
        if not len(containers):
            logger.warning("No container to start !")
            return
        for container in containers:
            logger.info(f"Starting container {container.name}")
            container.start()

    def stop(self, timeout: int = 10) -> None:
        """
        Stop Stack

        Args:
            timeout (int, optional): timeout before sending SIGKILL. Defaults to 10.

        Raises:
            StackNotFoundError: When stack does not exists
        """
        if not self.exists:
            raise StackNotFoundError(f"Stack {self.name} does not exists !")
        containers = self.containers()
        if not len(containers):
            logger.warning("No container to stop !")
            return
        for container in containers:
            logger.info(f"Stopping container {container.name}")
            container.stop(timeout=timeout)

    def restart(self, timeout: int = 10) -> None:
        """
        Restart Stack

        Args:
            timeout (int, optional): timeout before sending SIGKILL. Defaults to 10.

        Raises:
            StackNotFoundError: When stack does not exists
        """
        if not self.exists:
            raise StackNotFoundError(f"Stack {self.name} does not exists !")
        containers = self.containers()
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
        """
        Check state and return it

        Returns:
            StackState: Current Stack state
        """
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

    def __repr__(self):
        """
        Stack repr
        """
        return f"<Stack: {self.name}>"

    def __eq__(self, other: "Stack") -> bool:
        """
        Check if Stack equal other Stack

        Args:
            other (Stack): Other Stack instance

        Returns:
            bool:
        """
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name
