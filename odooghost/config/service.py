import abc
import typing as t

from pydantic import BaseModel

from . import db, odoo


class StackServiceConfig(BaseModel, abc.ABC):
    """
    Abstract config for stack services
    """

    service_port: t.Optional[int] = None
    """
    Map local port to container sercice port
    """


class StackServicesConfig(BaseModel):
    """
    Stack services configuration
    """

    odoo: odoo.OdooStackConfig
    """
    Odoo stack config
    """
    db: db.PostgresStackConfig
    """
    Database stack config
    """
