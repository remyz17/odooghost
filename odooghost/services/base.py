import abc

from docker.errors import APIError, ImageNotFound, NotFound
from loguru import logger

from odooghost import constant, exceptions
from odooghost.context import ctx


def labels_as_list(labels: dict[str, str]) -> list[str]:
    return [f"{k}={v}" for k, v in labels.items()]


class BaseService(abc.ABC):
    def __init__(self, name: str, stack_name: str) -> None:
        self.name = name
        self.stack_name = stack_name

    @abc.abstractmethod
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

    @abc.abstractmethod
    def build_image(self, rm: bool = True, no_cache: bool = False) -> None:
        if not self.has_custom_image:
            return None

    @abc.abstractmethod
    def drop_image(self) -> None:
        if self.has_custom_image:
            try:
                ctx.docker.images.remove(image=self.image_tag)
            except NotFound:
                logger.warning(f"Image {self.image_tag} not found !")
            except APIError as err:
                logger.error(f"Failed to drop image {self.image_tag}: {err}")

    @abc.abstractmethod
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

    @abc.abstractmethod
    def drop_volumes(self) -> None:
        try:
            volume = ctx.docker.volumes.get(self.volume_name)
            volume.remove()
        except NotFound:
            logger.warning(f"Volume {self.volume_name} not found !")
        except APIError as err:
            logger.error(f"Failed to drop volume {volume.id}: {err}")

    @abc.abstractmethod
    def create_container(self) -> None:
        ...

    @abc.abstractmethod
    def drop_containers(self, all: bool = True, force: bool = True) -> None:
        for container in ctx.docker.containers.list(
            all=all,
            filters={"label": labels_as_list(self._get_container_labels())},
        ):
            try:
                container.remove(force=force)
            except APIError as err:
                logger.error(f"Failed to drop container {container.id}: {err}")

    @abc.abstractmethod
    def create(self, do_pull: bool) -> None:
        self.ensure_base_image(do_pull=do_pull)
        self.build_image()
        self.create_volumes()
        self.create_container()

    @abc.abstractmethod
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
