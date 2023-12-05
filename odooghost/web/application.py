from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from strawberry.asgi import GraphQL

from odooghost.web.api.schema import schema


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
    app = Starlette(middleware=middleware)

    app.add_route("/graphql", graphql_app)
    app.add_websocket_route("/graphql", graphql_app)

    return app
