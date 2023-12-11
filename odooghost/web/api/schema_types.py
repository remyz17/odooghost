import enum

import strawberry

from odooghost import stack


@strawberry.enum
class StackState(enum.Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    RESTARTING = "RESTARTING"
    PAUSED = "PAUSED"


@strawberry.type
class Stack:
    name: str
    instance: strawberry.Private[stack.Stack]

    @strawberry.field
    def state(self) -> StackState:
        containers = self.instance.containers(stopped=True)
        if all(c.is_running for c in containers):
            return StackState.RUNNING
        if all(c.is_paused for c in containers):
            return StackState.PAUSED
        if any(c.is_restarting for c in containers):
            return StackState.RESTARTING
        return StackState.STOPPED

    @classmethod
    def from_instance(cls, instance: stack.Stack) -> "Stack":
        return cls(name=instance.name, instance=instance)
