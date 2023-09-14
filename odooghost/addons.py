import typing as t
from pathlib import Path

from odooghost import exceptions
from odooghost.config import AddonsConfig


class AddonsManager:
    def __init__(self, addons_config: t.List[AddonsConfig]) -> None:
        self._addons_config = addons_config

    @staticmethod
    def is_addons_path(addons_path: Path) -> bool:
        return True

    def _get_addons(
        self, mode: t.Optional[str] = None
    ) -> t.Generator[AddonsConfig, None, None]:
        for addon_config in self._addons_config:
            if mode is None:
                yield addon_config
            elif addon_config.mode == mode:
                yield addon_config

    def get_copy_addons(self) -> t.Generator[AddonsConfig, None, None]:
        yield from self._get_addons(mode="copy")

    def get_mount_addons(self) -> t.Generator[AddonsConfig, None, None]:
        yield from self._get_addons(mode="mount")

    def get_addons_path(self) -> str:
        return ",".join(
            map(lambda addons: addons.container_posix_path, self._get_addons())
        )

    def ensure(self) -> None:
        for addons in self.get_copy_addons():
            if not self.__class__.is_addons_path(addons_path=addons.path):
                raise exceptions.InvalidAddonsPathError(
                    f"Addons path {addons.path.as_posix()} is not a valid addons path"
                )

    @property
    def has_copy_addons(self) -> bool:
        return any(addon_config.mode == "copy" for addon_config in self._addons_config)

    @property
    def has_mount_addons(self) -> bool:
        return any(addon_config.mode == "mount" for addon_config in self._addons_config)
