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
        copy_addons = list(self._addons.get_copy_addons())
        if len(copy_addons):
            copy_addons_path = self.build_context_path / "addons"
            copy_addons_path.mkdir()
            for addons_path in copy_addons:
                src_path = addons_path.local_path
                dst_path = copy_addons_path / addons_path.name_hash
                logger.debug(f"Copying {src_path.as_posix()} to {dst_path.as_posix()}")
                shutil.copytree(
                    src=src_path,
                    dst=dst_path,
                )
        with open((self.build_context_path / "Dockerfile").as_posix(), "w") as stream:
            logger.debug("Rendering Dockerfile ...")
            stream.write(
                renderer.render_dockerfile(
                    odoo_version=self._config.version,
                    apt_dependencies=self._config.dependencies.apt,
                    pip_dependencies=self._config.dependencies.python,
                    copy_addons=copy_addons,
                )
            )

    def create_container(self) -> Container:
        # TODO create get container create options method
        return super().create_container(
            name=self.container_name,
            image=self.image_tag,
            hostname="odoo",
            labels=self.labels(),
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
