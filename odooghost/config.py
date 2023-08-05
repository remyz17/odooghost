import re
import typing as t

from pydantic import BaseModel, validator


class PostgresStackConfig(BaseModel):
    type: t.Literal["local", "remote"]
    version: int
    host: t.Optional[str] = None
    user: t.Optional[str] = None
    db: t.Optional[str] = None
    password: t.Optional[str] = None


class DependenciesConfig(BaseModel):
    apt: t.Optional[t.List[str]] = None
    python: t.Optional[t.List[str]] = None

    @validator("apt", "python", pre=True)
    def string_to_list(cls, v) -> t.List[str]:
        return v.split(" ")


class AddonsConfig(BaseModel):
    type: t.Literal["remote", "local"]
    origin: t.Optional[str] = None
    branch: t.Optional[str] = None
    path: t.Optional[str] = None


class OdooStackConfig(BaseModel):
    version: float
    cmdline: t.Optional[str] = None
    addons: t.List[AddonsConfig] = []
    dependencies: DependenciesConfig = DependenciesConfig()

    @validator("version")
    def validate_versîon(cls, v) -> float:
        if v not in (9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0):
            raise ValueError(f"Unsuported Odoo version {v}")
        return v


class StackConfig(BaseModel):
    name: str
    odoo: OdooStackConfig
    postgres: PostgresStackConfig

    @validator("name")
    def validate_name(cls, v) -> str:
        if " " in v or not re.match(r"^[\w-]+$", v):
            raise ValueError("Stack name must not contain spaces or special characters")
        return v
