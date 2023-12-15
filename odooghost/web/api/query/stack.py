import typing as t

import strawberry

from odooghost import constant
from odooghost.container import Container
from odooghost.stack import Stack
from odooghost.utils.misc import labels_as_list
from odooghost.web.api import schema_types


@strawberry.type
class Query:
    @strawberry.field
    def stack_count(self) -> int:
        return Stack.count()

    @strawberry.field
    def stack(self, name: str) -> schema_types.Stack:
        return schema_types.Stack.from_instance(Stack.from_name(name=name))

    @strawberry.field
    def stacks(self) -> t.List[schema_types.Stack]:
        return [schema_types.Stack.from_instance(stack) for stack in Stack.list()]

    @strawberry.field
    def containers(self, stopped: bool = True) -> t.List[schema_types.Container]:
        return [
            schema_types.Container.from_instance(c)
            for c in Container.search(
                filters={
                    "label": labels_as_list(
                        {
                            constant.LABEL_NAME: "true",
                        }
                    )
                },
                stopped=stopped,
            )
        ]
