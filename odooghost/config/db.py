import typing as t

from . import service


class PostgresStackConfig(service.StackServiceConfig):
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
