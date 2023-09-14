import shutil
import typing as t

from docker.types import Mount
from loguru import logger

from odooghost import addons, constant, renderer
from odooghost.container import Container

from .base import BaseService

if t.TYPE_CHECKING:
    from odooghost import config


class OdooService(BaseService):
    def __init__(self, stack_name: str, config: "config.OdooStackConfig") -> None:
        self._config = config
        self._addons = addons.AddonsManager(addons_config=config.addons)
        super().__init__(name="odoo", stack_name=stack_name)

    def _prepare_build_context(self) -> None:
        super()._prepare_build_context()
        if self._addons.has_copy_addons:
            copy_addons_path = self.build_context_path / "addons"
            copy_addons_path.mkdir()
            for addons_path in self._addons.get_copy_addons():
                src_path = addons_path.local_path
                dst_path = copy_addons_path / addons_path.name_hash
                logger.debug(f"Copying {src_path.as_posix()} to {dst_path.as_posix()}")
                shutil.copytree(
                    src=src_path,
                    dst=dst_path,
                )
        if self._config.dependencies.python.files:
            requirments_path = self.build_context_path / "requirments"
            requirments_path.mkdir()
            for requirments_file in self._config.dependencies.python.files:
                dst_path = (
                    requirments_path
                    / self._config.dependencies.python.get_file_hash(requirments_file)
                )
                logger.debug(
                    f"Copying {requirments_file.as_posix()} to {dst_path.as_posix()}"
                )
                shutil.copyfile(
                    src=requirments_file,
                    dst=dst_path,
                )
        with open((self.build_context_path / "Dockerfile").as_posix(), "w") as stream:
            logger.debug("Rendering Dockerfile ...")
            stream.write(
                renderer.render_dockerfile(
                    odoo_version=self._config.version,
                    dependencies=self._config.dependencies,
                    copy_addons=self._addons.has_copy_addons
                    and list(self._addons.get_copy_addons())
                    or None,
                    mount_addons=self._addons.has_mount_addons,
                )
            )

    def _get_cmdline(self) -> str:
        cmdline = ""
        if (
            self._config.cmdline.startswith("odoo")
            or self._config.cmdline.startswith("--")
            or self._config.cmdline.startswith("-")
        ):
            cmdline = self._config.cmdline
        else:
            return self._config.cmdline
        return f"{cmdline} --addons-path={self._addons.get_addons_path()}"

    def create_container(self) -> Container:
        # TODO create get container create options method
        return super().create_container(
            name=self.container_name,
            image=self.image_tag,
            hostname="odoo",
            labels=self.labels(),
            command=self._get_cmdline(),
            environment={
                "HOST": "db",
                "USER": "odoo",
                "PASSWORD": "odoo",
            },
            mounts=[
                Mount(
                    source=self.volume_name,
                    target="/var/lib/odoo",
                    type="volume",
                )
            ],
            network=constant.COMMON_NETWORK_NAME,
            tty=True,
        )

    def create(self, do_pull: bool, ensure_addons: bool) -> None:
        if ensure_addons:
            self._addons.ensure()
        return super().create(do_pull)

    @property
    def base_image_tag(self) -> str:
        return f"odoo:{self._config.version}"

    @property
    def image_tag(self) -> str:
        return f"odooghost_{self.stack_name}:{self._config.version}".lower()

    @property
    def has_custom_image(self) -> bool:
        return True
