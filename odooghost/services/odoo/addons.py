import os
import typing as t
from pathlib import Path

from loguru import logger

from odooghost.context import ctx
from odooghost.git import Git

if t.TYPE_CHECKING:
    from odooghost.config.addons import AddonsConfig


class AddonsHandler:
    def __init__(
        self, odoo_version: float, addons_config: t.List["AddonsConfig"]
    ) -> None:
        self.odoo_version = odoo_version
        self.addons = addons_config

    def _get_addons(
        self, mode: t.Optional[str] = None
    ) -> t.Generator["AddonsConfig", None, None]:
        for addon_config in self.addons:
            if mode is None:
                yield addon_config
            elif addon_config.mode == mode:
                yield addon_config

    def get_copy_addons(self) -> t.Generator["AddonsConfig", None, None]:
        """
        Yields addons configurations that are set to copy mode.

        Returns:
            t.Generator[AddonsConfig, None, None]: Copy addons
        """
        yield from self._get_addons(mode="copy")

    def get_mount_addons(self) -> t.Generator["AddonsConfig", None, None]:
        """
        Yields addons configurations that are set to mount mode.

        Returns:
            t.Generator[AddonsConfig, None, None]: Mount addons
        """
        yield from self._get_addons(mode="mount")

    def get_addons_path(self) -> str:
        """
        Returns configured roots and recursively discovered module parent paths.

        Returns:
            str: addons paths
        """
        addons_path = []
        for addon in self._get_addons():
            path = addon.path or self.get_context_path(addon)
            addons_path.append(addon.container_posix_path)
            for directory, subdirectories, filenames in os.walk(path):
                subdirectories[:] = sorted(
                    name
                    for name in subdirectories
                    if not name.startswith(".") and name != "__pycache__"
                )
                if not {"__manifest__.py", "__openerp__.py"}.intersection(filenames):
                    continue
                subdirectories.clear()
                relative_path = Path(directory).relative_to(path)
                if relative_path != Path("."):
                    addons_path.append(
                        (Path(addon.container_posix_path) / relative_path.parent)
                        .as_posix()
                    )
        addons_path = list(dict.fromkeys(addons_path))
        logger.info(addons_path)
        return ",".join(addons_path)

    def get_requirements_files(self) -> t.List[Path]:
        files = []
        for addon in self._get_addons():
            path = addon.path or self.get_context_path(addon)
            for directory, subdirectories, filenames in os.walk(path):
                subdirectories[:] = sorted(
                    name
                    for name in subdirectories
                    if not name.startswith(".") and name != "__pycache__"
                )
                if "requirements.txt" in filenames:
                    files.append((Path(directory) / "requirements.txt").resolve())
        return list(dict.fromkeys(files))

    def get_context_path(self, addons_config: "AddonsConfig") -> Path:
        real_path = ctx.config.working_dir / str(self.odoo_version) / addons_config.org
        if not real_path.exists():
            real_path.mkdir(parents=True)

        return real_path / addons_config.name

    def ensure(self) -> None:
        """
        Validates the addons paths, raising an error for invalid paths.
        Clone repo for addons of type remote if not already done.

        Raises:
            exceptions.InvalidAddonsPathError: When addons path is not valid
        """
        logger.info("Ensuring Odoo addons")
        for addons in self._get_addons():
            logger.debug(f"Validating addons {addons.name}")
            addons.validate()
            if addons.type == "remote":
                path = addons.path or self.get_context_path(addons)
                if path.exists():
                    continue
                Git.clone(
                    path=path,
                    url=addons.origin.url,
                    branch=addons.branch or str(self.odoo_version),
                    shallow=addons.shallow,
                )

    def pull(self, depth: int = 1) -> None:
        """
        Pull Odoo addons of type remote

        Args:
            depth (int, optional): git pull depth. Defaults to 1.
        """
        logger.info("Pulling Odoo addons ...")
        for addons in self._get_addons():
            addons.validate()
            if addons.type == "remote":
                path = addons.path or self.get_context_path(addons)
                if path.exists():
                    Git.pull(
                        path=path,
                        branch=addons.branch or str(self.odoo_version),
                        depth=depth,
                    )
                else:
                    Git.clone(
                        path=path,
                        url=addons.origin.url,
                        branch=addons.branch or str(self.odoo_version),
                        depth=depth,
                        shallow=addons.shallow,
                    )

    @property
    def has_copy_addons(self) -> bool:
        """
        Checks if any addons is set to copy mode.

        Returns:
            bool:
        """
        return any(addon_config.mode == "copy" for addon_config in self.addons)

    @property
    def has_mount_addons(self) -> bool:
        """
        Checks if any addons is set to mount mode.


        Returns:
            bool:
        """
        return any(addon_config.mode == "mount" for addon_config in self.addons)
