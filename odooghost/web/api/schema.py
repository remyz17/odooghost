import strawberry

from .query import dashboard, stack


@strawberry.type
class Query(dashboard.Query, stack.Query):
    ...


schema = strawberry.Schema(query=Query)
