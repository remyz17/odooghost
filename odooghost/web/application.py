import mimetypes

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope
from strawberry.asgi import GraphQL

from odooghost import constant
from odooghost.web.api.schema import schema

mimetypes.add_type("text/javascript", ".js")


async def not_found(request: Request, exc: HTTPException):
    return FileResponse((constant.STATIC_DIR / "index.html").as_posix())


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        if response.status_code == 404:
            response = await super().get_response("index.html", scope)
        return response


def create_app() -> Starlette:
    graphql_app = GraphQL(schema)
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
    app = Starlette(middleware=middleware, exception_handlers={404: not_found})

    app.add_route("/graphql", graphql_app)
    app.add_websocket_route("/graphql", graphql_app)
    app.mount(
        "/", app=SPAStaticFiles(directory=constant.STATIC_DIR.as_posix(), html=True)
    )

    return app
