from pathlib import Path

import docker
import yaml

from odooghost import constant, exceptions


class Context:
    def __init__(self) -> None:
        self._app_dir = constant.APP_DIR
        self._config_path = self._app_dir / "config.yml"
        self._data_dir = self._app_dir / "data"
        self._plugins_dir = self._app_dir / "plugins"
        self._docker_client = None

    def check_setup_state(self) -> bool:
        return self._app_dir.exists()

    def setup(self, version: str, working_dir: Path) -> None:
        if self.check_setup_state():
            raise exceptions.ContextAlreadySetupError("App already setup !")

        # TODO handle OSError
        for _dir in (self._app_dir, self._data_dir, self._plugins_dir):
            _dir.mkdir()
        config_data = dict(
            version=version, working_dir=working_dir.resolve().as_posix()
        )
        with open(self._config_path.as_posix(), "w") as stream:
            yaml.dump(config_data, stream=stream)

    @property
    def docker(self) -> docker.Client:
        if not self._docker_client:
            self._docker_client = docker.from_env()
        return self._docker_client


ctx = Context()
