import abc

from docker.errors import APIError, NotFound

from odooghost import exceptions
from odooghost.context import ctx


class BaseService(abc.ABC):
    def __init__(self) -> None:
        pass

    def ensure_image(self) -> None:
        try:
            ctx.docker.images.get(self.image_tag)
        except NotFound:
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

    @abc.abstractproperty
    def image_tag(self) -> str:
        ...
