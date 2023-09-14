import json
import re
import typing as t
from pathlib import Path

import yaml
from pydantic import BaseModel, field_serializer, model_validator, validator

from odooghost import exceptions
from odooghost.utils.misc import get_hash


class ContextConfig(BaseModel):
    """
    Context config holds configuration file
    """

    version: str
    """
    OdooGhost version
    """
    working_dir: Path
    """
    Working directory
    """


class PostgresStackConfig(BaseModel):
    type: t.Literal["local", "remote"]
    version: int
    host: t.Optional[str] = None
    user: t.Optional[str] = None
    db: t.Optional[str] = None
    password: t.Optional[str] = None


class PythonDependenciesConfig(BaseModel):
    list: t.Optional[t.List[str]] = None
    files: t.Optional[t.List[Path]] = None

    @field_serializer("files")
    def serialize_path(
        self, files: t.Optional[t.List[Path]]
    ) -> t.Optional[t.List[Path]]:
        if files is None:
            return files
        return [f.as_posix() for f in files]

    @classmethod
    def mount_path(cls) -> str:
        return "/mnt/pip-requirments"

    @classmethod
    def get_file_hash(cls, path: Path) -> str:
        return get_hash(path.as_posix())

    @classmethod
    def get_file_mount_path(cls, path: Path) -> str:
        return f"{cls.mount_path()}/{cls.get_file_hash(path=path)}"


class DependenciesConfig(BaseModel):
    apt: t.Optional[t.List[str]] = None
    python: t.Optional[PythonDependenciesConfig] = None

    @validator("apt", pre=True)
    def string_to_list(cls, v: str | list) -> t.List[str]:
        if isinstance(v, list):
            return v
        return v.split(" ")


class AddonsConfig(BaseModel):
    type: t.Literal["remote", "local"]
    mode: t.Literal["mount", "copy"]
    origin: t.Optional[str] = None
    branch: t.Optional[str] = None
    path: t.Optional[Path] = None

    @property
    def name(self) -> str:
        return self.path.name if self.type == "local" else self.origin

    @property
    def namespace(self) -> str:
        if self.type == "local":
            return f"local/{self.path.name}"
        elif self.type == "remote":
            return f"origin/{self.name}"

    # this should not run alaway as it would cause command like ls to fail if any addons does not exists anymore
    @model_validator(mode="after")
    def validate_addons_comfig(self) -> "AddonsConfig":
        if self.type == "local":
            if not self.path or not self.path.exists():
                raise ValueError(f"Provided addons path {self.path} does not exists")
            if self.branch or self.origin:
                raise ValueError(
                    f"Addons of type local can not handle {'branch' if self.branch else 'origin'}"
                )
        elif self.type == "remote":
            if self.branch is None or self.origin is None:
                raise ValueError(
                    f"Addons of type remote should have defined {'branch' if self.branch is None else 'origin'}"
                )
        return self

    @field_serializer("path")
    def serialize_path(self, path: Path) -> str:
        return path.as_posix()


class OdooStackConfig(BaseModel):
    version: float
    cmdline: t.Optional[str] = None
    addons: t.List[AddonsConfig] = []
    dependencies: DependenciesConfig = DependenciesConfig()

    @validator("version")
    def validate_versîon(cls, v: float) -> float:
        if v not in (9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0):
            raise ValueError(f"Unsuported Odoo version {v}")
        return v


class StackConfig(BaseModel):
    name: str
    odoo: OdooStackConfig
    postgres: PostgresStackConfig

    @validator("name")
    def validate_name(cls, v: str) -> str:
        if " " in v or not re.match(r"^[\w-]+$", v):
            raise ValueError("Stack name must not contain spaces or special characters")
        return v

    @classmethod
    def from_file(cls, file_path: Path) -> "StackConfig":
        """
        Return a StackConfig instance from JSON/YAML file config

        Args:
            file_path (Path): file path

        Raises:
            RuntimeError: when the file does not exists

        Returns:
            StackConfig: StackConfig instance
        """
        if not file_path.exists():
            # TODO replace this error
            raise RuntimeError("File does not exist")
        data = {}
        with open(file_path.as_posix(), "r") as stream:
            if file_path.name.endswith(".json"):
                data = json.load(fp=stream)
            elif file_path.name.endswith(".yml") or file_path.name.endswith(".yaml"):
                data = yaml.safe_load(stream=stream)
            else:
                raise exceptions.StackConfigError("Unsupported file format")
        return cls(**data)
