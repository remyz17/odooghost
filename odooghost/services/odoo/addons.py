import os
import typing as t
from pathlib import Path

from loguru import logger

from odooghost.context import ctx
from odooghost.git import Git, Repo

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
        Returns a comma-separated string of all addons paths.

        Returns:
            str: addons paths
        """
        addons_path = []
        for addon in self._get_addons():
            if addon.type != "remote":
                addons_path.append(addon.container_posix_path)
                continue
            path = addon.path or self.get_context_path(addon)
            repo = Repo(path.as_posix())
            if not repo.submodules:
                addons_path.append(addon.container_posix_path)
                continue
            submodule_paths = {sm.path for sm in repo.submodules}
            for rel_path in self._find_addons_dirs(path, exclude=submodule_paths):
                addons_path.append(
                    (Path(addon.container_posix_path) / rel_path).as_posix()
                )
            for sm_path in submodule_paths:
                addons_path.append(
                    (Path(addon.container_posix_path) / sm_path).as_posix()
                )
        logger.debug(f"Addons path: {addons_path}")
        return ",".join(addons_path)

    @staticmethod
    def _find_addons_dirs(
        root: Path, exclude: t.Set[str], max_depth: int = 3
    ) -> t.List[str]:
        """
        Find directories (relative to root, excluding submodules) that directly contain Odoo modules.
        """
        found = []
        for dirpath, dirnames, _ in os.walk(root):
            current = Path(dirpath)
            rel = current.relative_to(root).as_posix()
            if any((current / d / "__manifest__.py").is_file() for d in dirnames):
                found.append(rel)
                dirnames[:] = []
                continue
            depth = 0 if rel == "." else rel.count("/") + 1
            dirnames[:] = sorted(
                d
                for d in dirnames
                if not d.startswith(".")
                and d not in ("node_modules", "__pycache__")
                and (current / d).relative_to(root).as_posix() not in exclude
                and depth < max_depth
            )
        return found

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
