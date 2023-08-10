from pathlib import Path

import yaml
from loguru import logger

from odooghost import config, constant, services
from odooghost.context import ctx
from odooghost.exceptions import StackAlreadyExistsError


class Stack:
    def __init__(self, config: "config.StackConfig") -> None:
        self._config = config
        self._postgres_service = None
        self._odoo_service = None

    @classmethod
    def from_file(cls, file_path: Path) -> "Stack":
        if not file_path.exists():
            raise RuntimeError("File does not exist")
        data = {}
        with open(file_path.as_posix(), "r") as stream:
            data = yaml.safe_load(stream=stream)
        conf = config.StackConfig(**data)
        return cls(config=conf)

    @classmethod
    def ls(cls) -> None:
        pass

    @classmethod
    def ps(cls) -> None:
        pass

    @classmethod
    def search(cls) -> None:
        pass

    def _ensure_base_images(self, do_pull: bool = False) -> None:
        logger.info("Ensuring base images ...")
        self.postgres_service.ensure_base_image(do_pull=do_pull)
        self.odoo_service.ensure_base_image(do_pull=do_pull)

    def _build_images(self) -> None:
        logger.info("Building custom images ...")
        self.postgres_service.build_image()
        self.odoo_service.build_image()

    def _ensure_addons(self) -> None:
        pass

    def create(self, do_pull: bool = False, ensure_addons: bool = False) -> None:
        if self.exists:
            raise StackAlreadyExistsError(f"Stack {self.name} already exists !")
        self._ensure_base_images(do_pull=do_pull)
        self._build_images()
        if ensure_addons:
            self._ensure_addons()

    def drop(self) -> None:
        pass

    def update(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def restart(self) -> None:
        pass

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def odoo_service(self) -> "services.odoo.OdooService":
        if not self._odoo_service:
            self._odoo_service = services.odoo.OdooService(
                stack_name=self.name, config=self._config.odoo
            )
        return self._odoo_service

    @property
    def postgres_service(self) -> "services.postgres.PostgresService":
        if not self._postgres_service:
            self._postgres_service = services.postgres.PostgresService(
                stack_name=self.name, config=self._config.postgres
            )
        return self._postgres_service

    @property
    def exists(self) -> bool:
        return any(
            ctx.docker.containers.list(
                all=True, filters=dict(label=f"{constant.LABEL_STACKNAME}={self.name}")
            )
        )
