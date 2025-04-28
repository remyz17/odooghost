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
        Returns a comma-separated string of all addons paths.

        Returns:
            str: addons paths
        """
        return ",".join(
            map(lambda addons: addons.container_posix_path, self._get_addons())
        )

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
