import abc
import typing as t

from docker.errors import APIError, ImageNotFound, NotFound
from loguru import logger

from odooghost import constant, exceptions
from odooghost.container import Container
from odooghost.context import ctx
from odooghost.types import Filters, Labels
from odooghost.utils.docker import labels_as_list


class BaseService(abc.ABC):
    def __init__(self, name: str, stack_name: str) -> None:
        self.name = name
        self.stack_name = stack_name

    def _get_container_labels(self) -> dict[str, str]:
        return {
            constant.LABEL_NAME: "true",
            constant.LABEL_STACKNAME: self.stack_name,
            constant.LABEL_STACK_SERVICE_TYPE: self.name,
        }

    def ensure_base_image(self, do_pull: bool = False) -> None:
        logger.info(f"Ensuring image {self.base_image_tag}")
        try:
            ctx.docker.images.get(self.base_image_tag)
            if do_pull:
                ctx.docker.images.pull(self.base_image_tag)
        except ImageNotFound:
            try:
                ctx.docker.images.pull(self.base_image_tag)
            except APIError as err:
                raise exceptions.StackImagePullError(
                    f"Failed to pull image {self.base_image_tag}: {err}"
                )
        except APIError as err:
            raise exceptions.StackImageEnsureError(
                f"Failed to get image {self.base_image_tag}: {err}"
            )

    def build_image(self, rm: bool = True, no_cache: bool = False) -> None:
        if not self.has_custom_image:
            return None

    def drop_image(self) -> None:
        if self.has_custom_image:
            try:
                ctx.docker.images.remove(image=self.image_tag)
            except NotFound:
                logger.warning(f"Image {self.image_tag} not found !")
            except APIError as err:
                logger.error(f"Failed to drop image {self.image_tag}: {err}")

    def create_volumes(self) -> None:
        try:
            ctx.docker.volumes.create(
                name=self.volume_name,
                driver="local",
                labels={constant.LABEL_STACKNAME: self.stack_name},
            )
        except APIError as err:
            raise exceptions.StackVolumeCreateError(
                f"Failed to create {self.name} volume: {err}"
            )

    def drop_volumes(self) -> None:
        try:
            volume = ctx.docker.volumes.get(self.volume_name)
            volume.remove()
        except NotFound:
            logger.warning(f"Volume {self.volume_name} not found !")
        except APIError as err:
            logger.error(f"Failed to drop volume {volume.id}: {err}")

    def containers(
        self,
        filters: t.Optional[Filters] = None,
        labels: t.Optional[Labels] = None,
        stopped: bool = True,
    ) -> t.List[Container]:
        if filters is None:
            filters = {}
        filters.update(
            {
                "label": labels_as_list(self._get_container_labels())
                + (labels_as_list(labels) if labels else [])
            }
        )
        return list(
            filter(
                None,
                [
                    Container.from_ps(container)
                    for container in ctx.docker.api.containers(
                        all=stopped, filters=filters
                    )
                ],
            )
        )

    @abc.abstractmethod
    def create_container(self, **options) -> Container:
        return Container.create(**options)

    def drop_containers(self, all: bool = True, force: bool = True) -> None:
        for container in self.containers(stopped=all):
            try:
                container.remove(force=force)
            except APIError as err:
                logger.error(f"Failed to drop container {container.id}: {err}")

    def get_container(self) -> Container:
        try:
            return Container.from_id(id=self.container_name)
        except NotFound:
            raise exceptions.StackContainerNotFound(
                f"Container {self.container_name} not found !"
            )
        except APIError as err:
            raise exceptions.StackContainerGetError(
                f"Failed to get container {self.container_name} : {err}"
            )

    def start_container(self) -> Container:
        container = self.get_container()
        try:
            container.start()
            return container
        except APIError:
            raise exceptions.StackContainerStartError(
                f"Failed to start container {container.id}"
            )

    def create(self, do_pull: bool) -> None:
        self.ensure_base_image(do_pull=do_pull)
        self.build_image()
        self.create_volumes()
        self.create_container()

    def drop(self, volumes: bool = True) -> None:
        self.drop_containers()
        if volumes:
            self.drop_volumes()
        self.drop_image()

    @abc.abstractproperty
    def base_image_tag(self) -> str:
        ...

    @property
    def image_tag(self) -> str:
        raise NotImplementedError()

    @abc.abstractproperty
    def has_custom_image(self) -> bool:
        ...

    @property
    def volume_name(self) -> str:
        return f"odooghost_{self.stack_name}_{self.name}_data"

    @property
    def container_name(self) -> str:
        return f"odooghost_{self.stack_name}_{self.name}"

    @property
    def container_hostname(self) -> str:
        return f"{self.stack_name}-{self.name}"
