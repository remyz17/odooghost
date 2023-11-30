import typing as t
from pathlib import Path

from pydantic import BaseModel, field_serializer, field_validator, model_validator

from odooghost import exceptions, types
from odooghost.utils.misc import get_hash


def is_addons_path(config: "AddonsConfig") -> bool:
    return True


class AddonsConfig(BaseModel):
    """
    Addons config hold configurations for one addons path
    """

    type: t.Optional[types.AddonsType] = None
    """
    Type of addons path
    """
    mode: t.Literal["mount", "copy"] = "mount"
    """
    Addons path mode
    """
    origin: t.Optional[types.GitOrigin] = None
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
        return self.path.name if self.type == "local" else self.origin.name

    @property
    def org(self) -> str:
        """
        Get addons org

        Returns:
            str: addons name
        """
        return self.origin.owner

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
        path_hash = get_hash(
            self.path.as_posix() if self.type == "local" else self.origin.url
        )
        return f"{self.name}_{path_hash}"

    @property
    def container_posix_path(self) -> str:
        """
        Build container path

        Returns:
            str: container path
        """
        return f"/mnt/{self.mode}-addons/{self.name_hash}"

    def validate(self) -> None:
        """
        Validate addons path

        Raises:
            exceptions.InvalidAddonsPathError:
        """
        if not is_addons_path(self.path):
            raise exceptions.InvalidAddonsPathError(
                f"Addons path {self.path.as_posix()} is not a valid addons path"
            )

    @field_serializer("path")
    def serialize_path(self, path: Path) -> str:
        """
        Serialize path as string

        Args:
            path (Path): Path

        Returns:
            str: Serialized path
        """
        if path is None:
            return None
        return path.as_posix()

    @field_serializer("origin")
    def serialize_origin(self, origin: t.Optional[types.GitOrigin]) -> str:
        """
        Serialize origin as string

        Args:
            origin (types.GitUrl)

        Returns:
            str: Serialized origin
        """
        if origin is None:
            return None
        return origin.url

    @model_validator(mode="before")
    @classmethod
    def validate_type(cls, values) -> t.Any:
        # Accès et validation de plusieurs champs
        addon_type = values.get("type")
        origin = values.get("origin")

        if addon_type is None:
            values["type"] = "remote" if origin else "local"

        return values

    @model_validator(mode="after")
    def validate_addons(self) -> "AddonsConfig":
        if self.type == "local":
            if not self.path:
                raise ValueError("Addons of type local should have defined path !")
            if self.branch or self.origin:
                raise ValueError(
                    f"Addons of type local can not handle {'branch' if self.branch else 'origin'}"
                )
        elif self.type == "remote":
            if self.origin is None:
                raise ValueError("Addons of type remote should have defined origin !")
            if self.origin and not self.origin.valid:
                raise ValueError(f"Invalid git origin {self.origin.url}")
        return self

    @field_validator("path")
    @classmethod
    def validate_path(cls, v):
        # Vous pouvez accéder aux autres champs via `values` si nécessaire
        if v is not None:
            return v.expanduser().resolve()
        return v
