import sys
import typing as t
from io import BytesIO

from loguru import logger

from odooghost import exceptions, renderer, utils
from odooghost.context import ctx

from .base import BaseService

if t.TYPE_CHECKING:
    from odooghost import config


class OdooService(BaseService):
    def __init__(self, stack_name: str, config: "config.OdooStackConfig") -> None:
        self.stack_name = stack_name
        self._config = config
        super().__init__()

    def build_image(self) -> None:
        super().build_image()
        logger.debug("Building Odoo custom image")
        try:
            all_events = list(
                utils.progress_stream.stream_output(
                    ctx.docker.api.build(
                        fileobj=BytesIO(
                            renderer.render_dockerfile(
                                odoo_version=self._config.version,
                                apt_dependencies=self._config.dependencies.apt,
                                pip_dependencies=self._config.dependencies.python,
                            ).encode("utf-8")
                        ),
                        tag=self.image_tag,
                    ),
                    sys.stdout,
                )
            )
            print(all_events)
        except exceptions.StreamOutputError:
            raise exceptions.StackImageBuildError(
                "Failed to build Odoo image, check dependencies"
            )

    @property
    def base_image_tag(self) -> str:
        return f"odoo:{self._config.version}"

    @property
    def image_tag(self) -> str:
        return f"odooghost_{self.stack_name}:{self._config.version}".lower()

    @property
    def has_custom_image(self) -> bool:
        return True
