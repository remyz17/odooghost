import json
import typing as t
from pathlib import Path

import docker
import yaml
from docker.errors import APIError, NotFound

from odooghost import constant, exceptions
from odooghost.config import ContextConfig, StackConfig


class StackContext:
    def __init__(self, working_dir: Path) -> None:
        self._working_dir = working_dir

    def _write(self, config: StackConfig) -> None:
        with open(self.get_path(config.name), "w") as stream:
            json.dump(config.model_dump(), stream)

    def get_path(self, stack_name: str) -> Path:
        """
        Get Stack config path

        Args:
            stack_name (str): name of stack

        Returns:
            Path: Stack config path
        """
        return self._working_dir / f"{stack_name}.json"

    def get(self, stack_name: str) -> StackConfig:
        """
        Get StackConfig

        Args:
            stack_name (str): name of stack

        Returns:
            StackConfig: Stack config instance
        """
        if stack_name not in self:
            raise exceptions.StackNotFoundError(
                f"Stack {stack_name} config file doest not exists"
            )
        return StackConfig.from_file(file_path=self.get_path(stack_name=stack_name))

    def create(self, config: StackConfig) -> None:
        """
        Create StackConfig file in context

        Args:
            config (StackConfig): Stack config

        Raises:
            exceptions.StackAlreadyExistsError: When stack config file exists
        """
        if config in self:
            raise exceptions.StackAlreadyExistsError(
                f"Stack {config.name} already exists"
            )
        self._write(config=config)

    def update(self, config: StackConfig) -> None:
        """
        Update StackConfig file in context

        Args:
            config (StackConfig): Stack config

        Raises:
            exceptions.StackNotFoundError: When stack config file does not exists
        """
        if config not in self:
            raise exceptions.StackNotFoundError(f"Stack {config.name} not found")
        self._write(config=config)

    def drop(self, stack_name: str) -> None:
        """
        Drop Stack from context

        Args:
            stack_name (str): name of stack
        """
        if stack_name not in self:
            raise exceptions.StackNotFoundError(
                f"Stack {stack_name} config file doest not exists"
            )
        path = self.get_path(stack_name=stack_name)
        path.unlink()

    def __contains__(self, stack: str | StackConfig) -> bool:
        """
        Check if given stack name or StackConfig exists in context

        Args:
            stack (str | StackConfig): Stack to check

        Returns:
            bool: When stack exists or not
        """
        stack_name = stack.name if isinstance(stack, StackConfig) else stack
        stack_name = f"{stack_name}.json"
        return any(stack_name == f.name for f in self._working_dir.iterdir())

    def __iter__(self) -> t.Iterable[StackConfig]:
        """
        Iter over StackConfig's

        Yields:
            Iterator[t.Iterable[StackConfig]]: Stack config iterable
        """
        for file_path in self._working_dir.iterdir():
            yield StackConfig.from_file(file_path=file_path)

    def __len__(self) -> int:
        return len(list(self._working_dir.iterdir()))


class Context:
    """
    Context holds contextual data for OdooGhost
    """

    def __init__(self) -> None:
        self._app_dir = constant.APP_DIR
        self._config_path = self._app_dir / "config.yml"
        self._stack_ctx = StackContext(self._app_dir / "stacks")
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
        for _dir in (
            self._app_dir,
            self._stack_ctx._working_dir,
            self._data_dir,
            self._plugins_dir,
        ):
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

    def get_build_context_path(self) -> Path:
        """
        Get build context path

        Returns:
            Path: Path to build context
        """
        return Path("/tmp/odooghost")  # nosec B108

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

    @property
    def stacks(self) -> StackContext:
        if not self._init:
            raise RuntimeError(
                "Can not get stack config manager before initialize has been done"
            )
        return self._stack_ctx


ctx = Context()
