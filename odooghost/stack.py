import re
import typing as t
from pathlib import Path

import yaml
from pydantic import BaseModel, validator


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

    @classmethod
    def from_file(cls, file_path: Path) -> "Stack":
        if not file_path.exists():
            raise RuntimeError("File does not exist")
        data = {}
        with open(file_path.as_posix(), "r") as stream:
            data = yaml.safe_load(stream=stream)
        config = StackConfig(**data)
        return cls(config=config)
