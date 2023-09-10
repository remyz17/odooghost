import dataclasses
import hashlib
import typing as t
from pathlib import Path

from odooghost import exceptions
from odooghost.config import AddonsConfig


@dataclasses.dataclass
class AddonsCopy:
    name: str
    local_path: Path

    @property
    def name_hash(self) -> str:
        # This is to ensure there is no duplicate names
        path_hash = hashlib.md5(
            self.local_path.as_posix().encode(), usedforsecurity=False
        ).hexdigest()[:8]
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

    def ensure(self) -> None:
        for addons in self.get_copy_addons():
            if not self.__class__.is_addons_path(addons_path=addons.local_path):
                raise exceptions.InvalidAddonsPathError(
                    f"Addons path {addons.local_path.as_posix()} is not a valid addons path"
                )
