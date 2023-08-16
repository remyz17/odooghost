from pathlib import Path

import yaml
from loguru import logger

from odooghost import config, constant, services
from odooghost.context import ctx
from odooghost.exceptions import StackAlreadyExistsError, StackNotFoundError


class Stack:
    """
    Stack manage differents Odoo stacks regarding it's config
    """

    def __init__(self, config: "config.StackConfig") -> None:
        self._config = config
        self._postgres_service = None
        self._odoo_service = None

    @classmethod
    def from_file(cls, file_path: Path) -> "Stack":
        """
        Return a Stack instance from YAML file config

        Args:
            file_path (Path): file path

        Raises:
            RuntimeError: when the file does not exists

        Returns:
            Stack: Stack instance
        """
        if not file_path.exists():
            # TODO replace this error
            raise RuntimeError("File does not exist")
        data = {}
        with open(file_path.as_posix(), "r") as stream:
            data = yaml.safe_load(stream=stream)
        conf = config.StackConfig(**data)
        return cls(config=conf)

    @classmethod
    def ls(cls) -> None:
        """
        List all stacks
        """

    @classmethod
    def ps(cls) -> None:
        """
        List all running stacks
        """

    @classmethod
    def search(cls) -> None:
        pass

    def _ensure_addons(self) -> None:
        pass

    def create(self, do_pull: bool = False, ensure_addons: bool = False) -> None:
        logger.info(f"Creating Stack {self.name} ...")
        if self.exists:
            raise StackAlreadyExistsError(f"Stack {self.name} already exists !")
        if ensure_addons:
            self._ensure_addons()
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
        pass

    def start(self, detach: bool = True, open_browser: bool = False) -> None:
        ...

    def stop(self) -> None:
        pass

    def restart(self) -> None:
        pass

    @property
    def name(self) -> str:
        """
        Return name of stack

        Returns:
            str: Stack name
        """
        return self._config.name

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
        return any(
            ctx.docker.api.images(
                filters={"label": f"{constant.LABEL_STACKNAME}={self.name}"}, quiet=True
            )
        )
