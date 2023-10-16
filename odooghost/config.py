import json
import re
import typing as t
from pathlib import Path

import yaml
from pydantic import BaseModel, field_serializer, model_validator, validator

from odooghost import constant, exceptions
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
    """
    Postgres stack configuration holds database configuration
    It support both remote and local databse
    """

    type: t.Literal["local", "remote"]
    """
    Type of database config
    """
    version: int
    """
    Database version
    """
    host: t.Optional[str] = None
    """
    Database hostname
    """
    user: t.Optional[str] = None
    """
    Database user
    """
    db: t.Optional[str] = "postgres"
    """
    Database template (only availible in local type)
    """
    password: t.Optional[str] = None
    """
    Database user password
    """


class PythonDependenciesConfig(BaseModel):
    """
    Python dependencies configuration holds Python dependencies
    It supports requirments files and simple list of dependencies
    Dependencies are installed with PIP
    """

    list: t.Optional[t.List[str]] = None
    """
    List of Python dependencies
    """
    files: t.Optional[t.List[Path]] = None
    """
    List of requirments file
    """

    @field_serializer("files")
    def serialize_path(
        self, files: t.Optional[t.List[Path]]
    ) -> t.Optional[t.List[Path]]:
        """
        Serialize files path as list of string

        Args:
            files (t.Optional[t.List[Path]]): files path

        Returns:
            t.Optional[t.List[Path]]: Serialized files path
        """
        if files is None:
            return files
        return [f.as_posix() for f in files]

    @classmethod
    def mount_path(cls) -> str:
        """
        Get requirments build context mount path

        Returns:
            str: mount path
        """
        return "/mnt/pip-requirments"

    @classmethod
    def get_file_hash(cls, path: Path) -> str:
        """
        Get requirments file hash from path

        Args:
            path (Path): requirments file path

        Returns:
            str: requirments file hash
        """
        return get_hash(path.as_posix())

    @classmethod
    def get_file_mount_path(cls, path: Path) -> str:
        """
        Get requirments file mount path

        Args:
            path (Path): requirments file path

        Returns:
            str: requirments file mount path
        """
        return f"{cls.mount_path()}/{cls.get_file_hash(path=path)}"


class DependenciesConfig(BaseModel):
    """
    Dependencies configuration holds both APT and Python dependencies
    """

    apt: t.Optional[t.List[str]] = None
    python: t.Optional[PythonDependenciesConfig] = None

    @validator("apt", pre=True)
    def string_to_list(cls, v: str | list) -> t.List[str]:
        """
        Convert apt dependencies string to list if needed

        Args:
            v (str | list): apt dependencies

        Returns:
            t.List[str]: List of apt dependencies
        """
        if isinstance(v, list):
            return v
        return v.split(" ")


class AddonsConfig(BaseModel):
    """
    Addons config hold configurations for one addons path
    """

    type: t.Literal["remote", "local"]
    """
    Type of addons path
    """
    mode: t.Literal["mount", "copy"]
    """
    Addons path mode
    """
    origin: t.Optional[str] = None
    """
    Addons path git origin (should be of type remote)
    """
    branch: t.Optional[str] = None
    """
    Addons path git branch (should be of type remote)
    """
    path: t.Optional[Path] = None
    """
    Addons path local path
    """

    @property
    def name(self) -> str:
        """
        Get addons name

        Returns:
            str: addons name
        """
        return (
            self.path.name
            if self.type == "local"
            else self.origin.split("/")[-1].removesuffix(".git")
        )

    @property
    def namespace(self) -> str:
        """
        Get addons namespace

        Returns:
            str: namespace
        """
        if self.type == "local":
            return f"local/{self.path.name}"
        elif self.type == "remote":
            return f"origin/{self.name}"

    @property
    def name_hash(self) -> str:
        """
        Generate hash from path
        This is to ensure there is no duplicate names

        Returns:
            str: name hash
        """
        path_hash = get_hash(self.path.as_posix())
        return f"{self.name}_{path_hash}"

    @property
    def container_posix_path(self) -> str:
        """
        Build container path

        Returns:
            str: container path
        """
        return f"/mnt/{self.mode}-addons/{self.name_hash}"

    # this should not run alaway as it would cause command like ls to fail if any addons does not exists anymore
    @model_validator(mode="after")
    def validate_addons_config(self) -> "AddonsConfig":
        """
        Validate addons config

        Raises:
            ValueError:

        Returns:
            AddonsConfig: _description_
        """
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
        """
        Serialize path as string

        Args:
            path (Path): Path

        Returns:
            str: Serialized path
        """
        return path.as_posix()


class OdooStackConfig(BaseModel):
    """
    Odoo stack configuration
    """

    version: float
    """
    Odoo version
    """
    cmdline: t.Optional[str] = None
    """
    Odoo-bin cmdline
    """
    addons: t.List[AddonsConfig] = []
    """
    Odoo addons configurations
    """
    dependencies: DependenciesConfig = DependenciesConfig()
    """
    Odoo dependencies configurations
    """

    @validator("version")
    def validate_versîon(cls, v: float) -> float:
        """
        Validate supported Odoo version

        Raises:
            ValueError: When provided version is not supported

        Returns:
            float: Odoo version
        """
        if v not in (11.0, 12.0, 13.0, 14.0, 15.0, 16.0):
            raise ValueError(f"Unsuported Odoo version {v}")
        return v


class StackServicesConfig(BaseModel):
    """
    Stack services configuration
    """

    odoo: OdooStackConfig
    """
    Odoo stack config
    """
    db: PostgresStackConfig
    """
    Database stack config
    """


class StackNetworkConfig(BaseModel):
    """
    Stack network config
    """

    mode: t.Literal["shared", "scoped"] = "shared"


class StackConfig(BaseModel):
    """
    Stack configuration
    """

    name: str
    """
    Name of stack
    """
    services: StackServicesConfig
    """
    Services of stack
    """
    network: StackNetworkConfig = StackNetworkConfig()
    """
    Network config
    """

    @validator("name")
    def validate_name(cls, v: str) -> str:
        """
        Validate stack name

        Args:
            v (str): Stack name

        Raises:
            ValueError: When stack name is not valid

        Returns:
            str: Stack name
        """
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

    def get_service_hostname(self, service: str) -> str:
        """
        Get given service name regatding netowrk.
        We do prefix the service name with the stack name
        if the stack network is shared with other.
        This is done to allow running multiple stack's at
        the same time with the same network

        Args:
            service (str): service name

        Returns:
            str: name of the given service
        """
        return (
            f"{self.name.lower()}-{service}"
            if self.network.mode == "shared"
            else service
        )

    def get_network_name(self) -> str:
        """
        Get netowkr name regarding network mode
        T

        Returns:
            str: Stack netowrk name
        """
        return constant.COMMON_NETWORK_NAME or f"{constant.LABEL_NAME}_{self.name}"
