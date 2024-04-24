import enum
import typing as t

import strawberry

from odooghost import container, stack


@strawberry.enum
class StackState(enum.Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    RESTARTING = "RESTARTING"
    PAUSED = "PAUSED"


@strawberry.enum
class ContainerState(enum.Enum):
    EXITED = "EXITED"
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    RESTARTING = "RESTARTING"
    PAUSED = "PAUSED"


@strawberry.type
class Container:
    id: str
    image: str
    name: str
    service: str
    instance: strawberry.Private[container.Container]

    @strawberry.field
    def state(self) -> ContainerState:
        if self.instance.is_running:
            return ContainerState.RUNNING
        if self.instance.is_restarting:
            return ContainerState.RESTARTING
        if self.instance.is_paused:
            return ContainerState.PAUSED
        if self.instance.is_exited and self.instance.exit_code != 0:
            return ContainerState.EXITED
        return ContainerState.STOPPED

    @classmethod
    def from_instance(cls, instance: container.Container) -> "Container":
        return cls(
            id=instance.id,
            image=instance.image,
            name=instance.name,
            service=instance.service,
            instance=instance,
        )


@strawberry.type
class Stack:
    id: str
    name: str
    instance: strawberry.Private[stack.Stack]

    @strawberry.field
    def odoo_version(self) -> float:
        return self.instance._config.services.odoo.version

    @strawberry.field
    def db_version(self) -> int:
        return self.instance._config.services.db.version

    @strawberry.field
    def network_mode(self) -> str:
        return self.instance._config.network.mode

    @strawberry.field
    def state(self) -> StackState:
        containers = self.instance.containers(stopped=True)
        if any(c.is_running for c in containers):
            return StackState.RUNNING
        if all(c.is_paused for c in containers):
            return StackState.PAUSED
        if any(c.is_restarting for c in containers):
            return StackState.RESTARTING
        return StackState.STOPPED

    @strawberry.field
    def containers(self, stopped: bool = True) -> t.Optional[t.List[Container]]:
        ctns = self.instance.containers(stopped=stopped)
        if not ctns:
            return None
        return [Container.from_instance(c) for c in ctns]

    @classmethod
    def from_instance(cls, instance: stack.Stack) -> "Stack":
        return cls(id=instance.id, name=instance.name, instance=instance)
