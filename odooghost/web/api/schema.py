import strawberry

from .mutation.stack import Mutation
from .query import dashboard, stack
from .subscription import Subscription


@strawberry.type
class Query(dashboard.Query, stack.Query):
    ...


schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
