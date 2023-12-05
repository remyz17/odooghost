import strawberry

from odooghost.stack import Stack
from odooghost.web.api import schema_types


@strawberry.type
class Query:
    @strawberry.field
    def stack(self, name: str) -> schema_types.Stack:
        s = Stack.from_name(name=name)
        return schema_types.Stack(name=s.name, instance=s)
