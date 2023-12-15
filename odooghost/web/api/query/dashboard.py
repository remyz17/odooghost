import strawberry

from odooghost import __version__
from odooghost.context import ctx


@strawberry.type
class Query:
    @strawberry.field
    def version(self) -> str:
        return __version__

    @strawberry.field
    def docker_version(self) -> str:
        return ctx.docker.version()["Version"]
