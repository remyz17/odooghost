import abc

from docker.errors import APIError, ImageNotFound

from odooghost import exceptions
from odooghost.context import ctx


class BaseService(abc.ABC):
    def __init__(self) -> None:
        pass

    def ensure_base_image(self, do_pull: bool = False) -> None:
        try:
            ctx.docker.images.get(self.image_tag)
            if do_pull:
                ctx.docker.images.pull(self.image_tag)
        except ImageNotFound:
            try:
                ctx.docker.images.pull(self.image_tag)
            except APIError as err:
                raise exceptions.StackImagePullError(
                    f"Failed to pull image {self.image_tag}: {err}"
                )
        except APIError as err:
            raise exceptions.StackImageEnsureError(
                f"Failed to get image {self.image_tag}: {err}"
            )

    @abc.abstractmethod
    def build_image(self) -> None:
        if not self.has_custom_image:
            return None

    @abc.abstractproperty
    def image_tag(self) -> str:
        ...

    @abc.abstractproperty
    def has_custom_image(self) -> bool:
        ...
