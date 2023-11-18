import typing as t
from pathlib import Path

from pydantic import BaseModel, field_serializer, model_validator, validator

from odooghost.utils.misc import get_hash

from . import service


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
        if isinstance(v, str):
            return v.split(" ")
        return v


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


class OdooStackConfig(service.StackServiceConfig):
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
        if v not in (11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0):
            raise ValueError(f"Unsuported Odoo version {v}")
        return v
