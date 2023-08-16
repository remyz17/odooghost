import typing as t
from pathlib import Path

import docker
import yaml
from docker.errors import APIError, NotFound
from pydantic import BaseModel

from odooghost import constant, exceptions


class ContextConfig(BaseModel):
    """
    Context config holds configuration file
    """

    version: str
    """
    OdooGhost version
    """
    working_dir: Path
    """
    Working directory
    """


class Context:
    """
    Context holds contextual data for OdooGhost
    """

    def __init__(self) -> None:
        self._app_dir = constant.APP_DIR
        self._config_path = self._app_dir / "config.yml"
        self._data_dir = self._app_dir / "data"
        self._plugins_dir = self._app_dir / "plugins"
        self._config: t.Optional[ContextConfig] = None
        self._docker_client: t.Optional[docker.DockerClient] = None
        self._init = False
        self.initialize()

    def check_setup_state(self) -> bool:
        """
        Check setup status

        Returns:
            bool
        """
        return self._app_dir.exists()

    def initialize(self) -> None:
        """
        Initialize context
        """
        if self.check_setup_state():
            with open(self._config_path.as_posix(), "r") as stream:
                self._config = ContextConfig(**yaml.safe_load(stream=stream))
            self._init = True

    def setup(self, version: str, working_dir: Path) -> None:
        """
        Setup OdooGhost

        Args:
            version (str): OdooGhost version
            working_dir (Path): working directory

        Raises:
            exceptions.ContextAlreadySetupError: Already setup
        """
        if self.check_setup_state():
            raise exceptions.ContextAlreadySetupError("App already setup !")

        # TODO handle OSError
        for _dir in (self._app_dir, self._data_dir, self._plugins_dir):
            _dir.mkdir()
        config_data = dict(
            version=version, working_dir=working_dir.resolve().as_posix()
        )
        with open(self._config_path.as_posix(), "w") as stream:
            yaml.safe_dump(config_data, stream=stream)

        self.initialize()

    def create_common_network(self) -> None:
        """
        Create common Docker network for stacks

        Raises:
            exceptions.CommonNetworkEnsureError: When create fail
        """
        try:
            self.docker.networks.create(
                name=constant.COMMON_NETWORK_NAME,
                driver="bridge",
                check_duplicate=True,
                attachable=True,
                scope="local",
            )
        except APIError:
            raise exceptions.CommonNetworkEnsureError("Failed to create common network")

    def ensure_common_network(self) -> None:
        """
        Ensure common Docker network

        Raises:
            exceptions.CommonNetworkEnsureError: When ensure fail
        """
        try:
            self.docker.networks.get(constant.COMMON_NETWORK_NAME)
        except NotFound:
            self.create_common_network()
        except APIError:
            raise exceptions.CommonNetworkEnsureError("Failed to ensure common network")

    @property
    def docker(self) -> "docker.DockerClient":
        """
        Lazyily return Docker client

        Returns:
            docker.DockerClient: Docker client instance
        """
        if not self._docker_client:
            self._docker_client = docker.from_env()
        return self._docker_client

    @property
    def config(self) -> ContextConfig:
        """
        Get context config

        Raises:
            RuntimeError: when context was not initialized

        Returns:
            ContextConfig: context config
        """
        if not self._init:
            raise RuntimeError("Can not get config before initialize has been done")
        return self._config


ctx = Context()
