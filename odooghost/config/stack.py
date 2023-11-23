import json
import re
import typing as t
from pathlib import Path

import yaml
from pydantic import BaseModel, field_validator

from odooghost import constant, exceptions

from . import service


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
    services: service.StackServicesConfig
    """
    Services of stack
    """
    network: StackNetworkConfig = StackNetworkConfig()
    """
    Network config
    """

    @field_validator("name")
    @classmethod
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
