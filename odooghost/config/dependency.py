import typing as t
from pathlib import Path

from pydantic import BaseModel, field_serializer, field_validator

from odooghost.utils.misc import get_hash


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
    apt_archived: bool = False
    python: t.Optional[PythonDependenciesConfig] = None
    custom_installations: t.Optional[t.List[str]] = None

    @field_validator("apt")
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
