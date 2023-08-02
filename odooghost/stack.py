import re
import typing as t
from pathlib import Path

import yaml
from pydantic import BaseModel, validator

from odooghost import services
from odooghost.context import ctx


class PostgresStackConfig(BaseModel):
    type: t.Literal["local", "remote"]
    version: int
    host: t.Optional[str] = None
    user: t.Optional[str] = None
    db: t.Optional[str] = None
    password: t.Optional[str] = None


class DependenciesConfig(BaseModel):
    apt: t.Optional[t.List[str]] = None
    python: t.Optional[t.List[str]] = None

    @validator("apt", "python", pre=True)
    def string_to_list(cls, v) -> t.List[str]:
        return v.split(" ")


class AddonsConfig(BaseModel):
    type: t.Literal["remote", "local"]
    origin: t.Optional[str] = None
    branch: t.Optional[str] = None
    path: t.Optional[str] = None


class OdooStackConfig(BaseModel):
    version: float
    cmdline: t.Optional[str] = None
    addons: t.List[AddonsConfig] = []
    dependencies: DependenciesConfig = DependenciesConfig()

    @validator("version")
    def validate_versîon(cls, v) -> float:
        if v not in (9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0):
            raise ValueError(f"Unsuported Odoo version {v}")
        return v


class StackConfig(BaseModel):
    name: str
    odoo: OdooStackConfig
    postgres: PostgresStackConfig

    @validator("name")
    def validate_name(cls, v) -> str:
        if " " in v or not re.match(r"^[\w-]+$", v):
            raise ValueError("Stack name must not contain spaces or special characters")
        return v


class Stack:
    def __init__(self, config: StackConfig) -> None:
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
        config = StackConfig(**data)
        return cls(config=config)

    @classmethod
    def ls(self) -> None:
        pass

    @classmethod
    def ps(self) -> None:
        pass

    def _ensure_images(self) -> None:
        for service in (self.odoo_service, self.postgres_service):
            service.ensure_image()

    def create(self) -> None:
        pass

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
            self._odoo_service = services.odoo.OdooService(config=self._config.odoo)
        return self._odoo_service

    @property
    def postgres_service(self) -> "services.postgres.PostgresService":
        if not self._postgres_service:
            self._postgres_service = services.postgres.PostgresService(
                config=self._config.postgres
            )
        return self._postgres_service

    @property
    def exits(self) -> bool:
        return any(
            ctx.docker.containers.list(
                all=True, filters=dict(label=f"odooshot_stackname={self.name}")
            )
        )
