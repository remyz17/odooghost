import dataclasses
import typing as t
from pathlib import Path

from odooghost import exceptions
from odooghost.config import AddonsConfig
from odooghost.utils.misc import get_hash


@dataclasses.dataclass
class AddonsCopy:
    name: str
    local_path: Path

    @property
    def name_hash(self) -> str:
        # This is to ensure there is no duplicate names
        path_hash = get_hash(self.local_path.as_posix())
        return f"{self.name}_{path_hash}"

    @property
    def container_posix_path(self) -> str:
        return f"/mnt/copy-addons/{self.name_hash}"


class AddonsManager:
    def __init__(self, addons_config: t.List[AddonsConfig]) -> None:
        self._addons_config = addons_config

    @staticmethod
    def is_addons_path(addons_path: Path) -> bool:
        return True

    def get_copy_addons(self) -> t.Generator[AddonsCopy, None, None]:
        for addon_config in self._addons_config:
            if addon_config.mode == "mount":
                continue
            yield AddonsCopy(name=addon_config.name, local_path=addon_config.path)

    def get_addons_path(self) -> str:
        return ",".join(
            map(lambda addons: addons.container_posix_path, self.get_copy_addons())
        )

    def ensure(self) -> None:
        for addons in self.get_copy_addons():
            if not self.__class__.is_addons_path(addons_path=addons.local_path):
                raise exceptions.InvalidAddonsPathError(
                    f"Addons path {addons.local_path.as_posix()} is not a valid addons path"
                )

    @property
    def has_copy_addons(self) -> bool:
        return any(addon_config.mode == "copy" for addon_config in self._addons_config)

    @property
    def has_mount_addons(self) -> bool:
        return any(addon_config.mode == "mount" for addon_config in self._addons_config)
