import shutil
import typing as t
from pathlib import Path

from docker.types import Mount
from loguru import logger

from odooghost import renderer
from odooghost.services.base import BaseService

from .addons import AddonsHandler

if t.TYPE_CHECKING:
    from odooghost import config

VOLUME_PATH: Path = Path("/var/lib/odoo")


def get_filestore_path(dbname: str) -> str:
    return (VOLUME_PATH / "filestore" / dbname).as_posix()


class OdooService(BaseService):
    name = "odoo"

    def __init__(self, stack_config: "config.StackConfig") -> None:
        super().__init__(stack_config=stack_config)
        self.addons = AddonsHandler(
            odoo_version=self.config.version, addons_config=self.config.addons
        )

    def _prepare_build_context(self) -> None:
        super()._prepare_build_context()
        if self.addons.has_copy_addons:
            copy_addons_path = self.build_context_path / "addons"
            copy_addons_path.mkdir()
            for addons_path in self.addons.get_copy_addons():
                src_path = addons_path.path or self.addons.get_context_path(addons_path)
                dst_path = copy_addons_path / addons_path.name_hash
                logger.debug(f"Copying {src_path.as_posix()} to {dst_path.as_posix()}")
                shutil.copytree(
                    src=src_path,
                    dst=dst_path,
                )
        if self.config.dependencies.python and self.config.dependencies.python.files:
            requirments_path = self.build_context_path / "requirments"
            requirments_path.mkdir()
            for requirments_file in self.config.dependencies.python.files:
                dst_path = (
                    requirments_path
                    / self.config.dependencies.python.get_file_hash(requirments_file)
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
                    odoo_version=self.config.version,
                    dependencies=self.config.dependencies,
                    copy_addons=self.addons.has_copy_addons
                    and list(self.addons.get_copy_addons())
                    or None,
                    mount_addons=self.addons.has_mount_addons,
                    addons_path=self.addons.get_addons_path(),
                )
            )

    def _get_mounts(self) -> t.List[Mount]:
        mounts = [
            Mount(
                source=self.volume_name,
                target=VOLUME_PATH.as_posix(),
                type="volume",
            )
        ]
        for addons_path in self.addons.get_mount_addons():
            mounts.append(
                Mount(
                    source=addons_path.path
                    and addons_path.path.as_posix()
                    or self.addons.get_context_path(addons_path).as_posix(),
                    target=addons_path.container_posix_path,
                    type="bind",
                )
            )
        return mounts

    def _get_environment(self) -> dict[str, any]:
        db_service_config = self.stack_config.services.db
        return dict(
            HOST=db_service_config.host
            or self.stack_config.get_service_hostname(service="db"),
            USER=db_service_config.user or "odoo",
            password=db_service_config.password or "odoo",
        )

    def _get_container_options(self, one_off: bool = False) -> t.Dict[str, t.Any]:
        options = super()._get_container_options(one_off)
        options.update(
            dict(
                command=self.config.cmdline,
                mounts=self._get_mounts(),
                tty=True,
            )
        )
        return options

    def create(self, force: bool, do_pull: bool, ensure_addons: bool, **kw) -> None:
        if ensure_addons:
            self.addons.ensure()
        return super().create(force=force, do_pull=do_pull, **kw)

    def pull(self) -> None:
        self.addons.pull()
        return super().pull()

    @property
    def config(self) -> "config.OdooStackConfig":
        return super().config

    @property
    def base_image_tag(self) -> str:
        return f"odoo:{self.config.version}"

    @property
    def image_tag(self) -> str:
        return f"odooghost_{self.stack_name}:{self.config.version}".lower()

    @property
    def has_custom_image(self) -> bool:
        return True

    @property
    def container_port(self) -> int:
        return 8069
