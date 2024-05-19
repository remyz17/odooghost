import typing as t

import strawberry

from odooghost import exceptions
from odooghost.stack import Stack


@strawberry.type
class StartStackSuccess:
    name: str


@strawberry.type
class StartStackError:
    message: str


StartStackResult = t.Annotated[
    StartStackSuccess | StartStackError,
    strawberry.union("StartStackResult"),
]


@strawberry.type
class StopStackSuccess:
    name: str


@strawberry.type
class StopStackError:
    message: str


StopStackResult = t.Annotated[
    StopStackSuccess | StopStackError,
    strawberry.union("StopStackResult"),
]


@strawberry.type
class RestartStackSuccess:
    name: str


@strawberry.type
class RestartStackError:
    message: str


RestartStackResult = t.Annotated[
    RestartStackSuccess | RestartStackError,
    strawberry.union("RestartStackResult"),
]


@strawberry.type
class Mutation:
    @strawberry.field
    def start_stack(self, name: str) -> StartStackResult:
        stack = Stack.from_name(name=name)
        try:
            stack.start()
            return StartStackSuccess(name=name)
        except exceptions.StackException as err:
            return StartStackError(message=str(err))

    @strawberry.field
    def stop_stack(self, name: str) -> StopStackResult:
        stack = Stack.from_name(name=name)
        try:
            stack.stop()
            return StopStackSuccess(name=name)
        except exceptions.StackException as err:
            return StopStackError(message=str(err))

    @strawberry.field
    def restart_stack(self, name: str) -> RestartStackResult:
        stack = Stack.from_name(name=name)
        try:
            stack.restart()
            return RestartStackSuccess(name=name)
        except exceptions.StackException as err:
            return RestartStackError(message=str(err))
