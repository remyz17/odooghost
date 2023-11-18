import typing as t
from pathlib import Path

from pydantic import BaseModel, field_serializer, model_validator

from odooghost.utils.misc import get_hash


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
