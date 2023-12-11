import typing as t

import strawberry

from odooghost.stack import Stack
from odooghost.web.api import schema_types


@strawberry.type
class Query:
    @strawberry.field
    def stack(self, name: str) -> schema_types.Stack:
        return schema_types.Stack.from_instance(Stack.from_name(name=name))

    @strawberry.field
    def stacks(self) -> t.List[schema_types.Stack]:
        return [schema_types.Stack.from_instance(stack) for stack in Stack.list()]
