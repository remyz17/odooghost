import abc
import typing as t

from pydantic import BaseModel, validator

from odooghost import exceptions

from . import addons as _addons
from . import dependency


class StackServiceConfig(BaseModel, abc.ABC):
    """
    Abstract config for stack services
    """

    service_port: t.Optional[int] = None
    """
    Map local port to container sercice port
    """


class PostgresStackConfig(StackServiceConfig):
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


class OdooStackConfig(StackServiceConfig):
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
    addons: t.List[_addons.AddonsConfig] = []
    """
    Odoo addons configurations
    """
    dependencies: dependency.DependenciesConfig = dependency.DependenciesConfig()
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

    def _get_addons(
        self, mode: t.Optional[str] = None
    ) -> t.Generator[_addons.AddonsConfig, None, None]:
        for addon_config in self.addons:
            if mode is None:
                yield addon_config
            elif addon_config.mode == mode:
                yield addon_config

    def get_copy_addons(self) -> t.Generator[_addons.AddonsConfig, None, None]:
        """
        Yields addons configurations that are set to copy mode.

        Returns:
            t.Generator[AddonsConfig, None, None]: Copy addons
        """
        yield from self._get_addons(mode="copy")

    def get_mount_addons(self) -> t.Generator[_addons.AddonsConfig, None, None]:
        """
        Yields addons configurations that are set to mount mode.

        Returns:
            t.Generator[AddonsConfig, None, None]: Mount addons
        """
        yield from self._get_addons(mode="mount")

    def get_addons_path(self) -> str:
        """
        Returns a comma-separated string of all addons paths.

        Returns:
            str: addons paths
        """
        return ",".join(
            map(lambda addons: addons.container_posix_path, self._get_addons())
        )

    def ensure_addons(self) -> None:
        """
        Validates the addons paths, raising an error for invalid paths.

        Raises:
            exceptions.InvalidAddonsPathError: When addons path is not valid
        """
        for addons in self._get_addons():
            addons.validate()
            if not _addons.is_addons_path(addons_path=addons.path):
                raise exceptions.InvalidAddonsPathError(
                    f"Addons path {addons.path.as_posix()} is not a valid addons path"
                )

    @property
    def has_copy_addons(self) -> bool:
        """
        Checks if any addons is set to copy mode.

        Returns:
            bool:
        """
        return any(addon_config.mode == "copy" for addon_config in self.addons)

    @property
    def has_mount_addons(self) -> bool:
        """
        Checks if any addons is set to mount mode.


        Returns:
            bool:
        """
        return any(addon_config.mode == "mount" for addon_config in self.addons)


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
