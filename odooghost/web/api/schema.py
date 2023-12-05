import strawberry

from .query import stack


@strawberry.type
class Query(stack.Query):
    ...


schema = strawberry.Schema(query=Query)
