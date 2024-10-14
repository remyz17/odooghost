import abc
import typing as t

from pydantic import BaseModel, field_validator

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

    @field_validator("version")
    @classmethod
    def validate_versîon(cls, v: float) -> float:
        """
        Validate supported Odoo version

        Raises:
            ValueError: When provided version is not supported

        Returns:
            float: Odoo version
        """
        if v not in (11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0):
            raise ValueError(f"Unsuported Odoo version {v}")
        return v


class MailStackConfig(StackServiceConfig):
    version: str = "latest"


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
    mail: t.Optional[MailStackConfig] = None
    """
    Optional mailhog config
    """
