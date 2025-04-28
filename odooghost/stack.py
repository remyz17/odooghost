import enum
import typing as t
from functools import wraps
from pathlib import Path

from loguru import logger

from odooghost import config, constant
from odooghost.container import Container
from odooghost.context import ctx
from odooghost.exceptions import StackAlreadyExistsError, StackNotFoundError
from odooghost.filters import OneOffFilter
from odooghost.services import db, mail, odoo
from odooghost.types import Filters, Labels
from odooghost.utils.misc import get_hash, labels_as_list

if t.TYPE_CHECKING:
    from odooghost.services.base import BaseService


class StackState(enum.Enum):
    """
    StackState obviously holds StackState
    """

    NONE: int = 0
    PARTIAL: int = 1
    READY: int = 2


# TODO ADD context manager
class Stack:
    """
    Stack manage differents Odoo stacks regarding it's config
    """

    def __init__(self, config: "config.StackConfig") -> None:
        self._config = config
        self._services: t.Dict[str, t.Type["BaseService"]] = dict(
            db=db.DbService(stack_config=config),
            odoo=odoo.OdooService(stack_config=config),
        )
        if config.services.mail:
            self._services.update(dict(mail=mail.MailService(stack_config=config)))

    def _check_state(self) -> StackState:
        """
        Check Stack state

        Returns:
            StackState: return current state
        """
        if self.name not in ctx.stacks:
            return StackState.NONE
        # TODO implement partial state
        return StackState.READY

    def _ensure_exists(func: t.Callable) -> t.Callable:
        """
        Ensure Stack exists

        Args:
            func (t.Callable): function to call

        Raises:
            StackNotFoundError: When Stack does not exists

        Returns:
            t.Callable: wrapped function
        """

        @wraps(func)
        def inner(self: "Stack", *args, **kwargs) -> t.Any:
            if not self.exists:
                raise StackNotFoundError(f"Stack {self.name} does not exists !")
            return func(self, *args, **kwargs)

        return inner

    @classmethod
    def from_file(cls, file_path: Path) -> "Stack":
        """
        Instanciate Stack from file

        File could be both YAML and JSON

        Args:
            file_path (Path): stack config file path

        Returns:
            Stack: Stack instance
        """
        return cls(config=config.StackConfig.from_file(file_path=file_path))

    @classmethod
    def from_name(cls, name: str) -> "Stack":
        """
        Instanciate Stack from name
        Stack config will be searched from Context

        Args:
            name (str): Stack name

        Returns:
            Stack: Stack instance
        """
        return cls(config=ctx.stacks.get(stack_name=name))

    @classmethod
    def count(cls) -> int:
        """
        Count all stacks in context

        Returns:
            int: stack count
        """
        return len(ctx.stacks)

    @classmethod
    def list(cls, running: bool = False) -> t.Generator["Stack", None, None]:
        """
        List all stacks

        Yields:
            Srack: Stack instance
        """
        # TODO implment running stack only
        if running:
            for stack_name in set(
                map(
                    lambda container: container.stack,
                    Container.search(
                        filters={
                            "label": labels_as_list(
                                {
                                    constant.LABEL_NAME: "true",
                                }
                            )
                        }
                    ),
                )
            ):
                yield cls.from_name(name=stack_name)

        else:
            for stack_config in ctx.stacks:
                yield cls(config=stack_config)

    def labels(self, one_off: OneOffFilter = OneOffFilter.exclude) -> Labels:
        """
        Get Stack labels

        Returns:
            Labels: Labels as dict
        """
        labels = {
            constant.LABEL_NAME: "true",
            constant.LABEL_STACKNAME: self.name,
        }
        OneOffFilter.update_labels(value=one_off, labels=labels)
        return labels

    def services(self) -> t.List[t.Type["BaseService"]]:
        return list(self._services.values())

    def get_service(self, name: str) -> t.Type["BaseService"]:
        try:
            service = self._services[name]
        except KeyError:
            # TODO make exception
            raise Exception
        return service

    def containers(
        self,
        filters: t.Optional[Filters] = None,
        labels: t.Optional[Labels] = None,
        stopped: bool = False,
        one_off: OneOffFilter = OneOffFilter.exclude,
    ) -> t.List[Container]:
        """
        Get Stack containers

        Args:
            filters (t.Optional[Filters], optional): Search filters. Defaults to None.
            labels (t.Optional[Labels], optional): Additionnal search labels. Defaults to None.
            stopped (bool, optional): Get stopped containers. Defaults to False.

        Returns:
            t.List[Container]: Container list
        """
        if filters is None:
            filters = {}
        filters.update(
            {
                "label": labels_as_list(self.labels(one_off=one_off))
                + (labels_as_list(labels) if labels else [])
            }
        )
        return Container.search(filters=filters, stopped=stopped)

    def create(
        self, force: bool = False, do_pull: bool = True, ensure_addons: bool = True
    ) -> None:
        """
        Create Stack

        Args:
            force (bool, optional): Force recreate of dangling containers. Defaults to False.
            do_pull (bool, optional): Pull base images. Defaults to True.
            ensure_addons (bool, optional): Ensure Odoo addons. Defaults to True.

        Raises:
            StackAlreadyExistsError: When Stack alreary exists
        """
        if self.exists:
            raise StackAlreadyExistsError(f"Stack {self.name} already exists !")
        logger.info(f"Creating Stack {self.name} ...")
        # TODO allow custom network
        ctx.ensure_common_network()
        for service in self.services():
            service.create(force=force, do_pull=do_pull, ensure_addons=ensure_addons)

        ctx.stacks.create(config=self._config)
        logger.info(f"Created Stack {self.name} !")

    @_ensure_exists
    def drop(self, volumes: bool = False) -> None:
        """
        Drop Stack

        Args:
            volumes (bool, optional): Drop volumes. Defaults to False.

        Raises:
            StackNotFoundError: When Stack does not exists
        """
        logger.info(f"Dropping Stack {self.name} ...")
        for service in self.services():
            service.drop(volumes=volumes)
        ctx.stacks.drop(stack_name=self.name)
        logger.info(f"Dropped Stack {self.name} !")

    @_ensure_exists
    def pull(self) -> None:
        """
        Pull Stack
        """
        logger.info(f"Pulling Stack {self.name} ...")
        for service in self.services():
            service.pull()
        logger.info(f"Pulled Stack {self.name} !")

    @_ensure_exists
    def update(self, do_pull: bool = False) -> None:
        """
        Update Stack
        """
        logger.info(f"Updating Stack {self.name} ...")
        for service in self.services():
            if do_pull:
                service.pull()
            service.update()
        ctx.stacks.update(config=self._config)
        logger.info(f"Updated Stack {self.name} !")

    @_ensure_exists
    def start(self) -> None:
        """
        Start Stack

        Raises:
            StackNotFoundError: When Stack does not exists
        """
        containers = self.containers(stopped=True)
        if not len(containers):
            logger.warning("No container to start !")
            return
        for container in containers:
            logger.info(f"Starting container {container.name}")
            container.start()

    @_ensure_exists
    def stop(self, timeout: int = 10, wait: bool = False) -> None:
        """
        Stop Stack

        Args:
            timeout (int, optional): timeout before sending SIGKILL. Defaults to 10.

        Raises:
            StackNotFoundError: When stack does not exists
        """
        containers = self.containers()
        if not len(containers):
            logger.warning("No container to stop !")
            return
        for container in containers:
            logger.info(f"Stopping container {container.name}")
            container.stop(timeout=timeout)
        if wait:
            logger.info("Waiting for containers to stop")
            for container in containers:
                container.wait()

    @_ensure_exists
    def restart(self, timeout: int = 10) -> None:
        """
        Restart Stack

        Args:
            timeout (int, optional): timeout before sending SIGKILL. Defaults to 10.

        Raises:
            StackNotFoundError: When stack does not exists
        """
        containers = self.containers()
        if not len(containers):
            logger.warning("No container to restart !")
            return
        for container in containers:
            logger.info(f"Restarting container {container.name}")
            container.restart(timeout=timeout)

    @property
    def name(self) -> str:
        """
        Return name of stack

        Returns:
            str: Stack name
        """
        return self._config.name

    @property
    def state(self) -> StackState:
        """
        Check state and return it

        Returns:
            StackState: Current Stack state
        """
        return self._check_state()

    @property
    def exists(self) -> bool:
        """
        Check if stack already exists

        Returns:
            bool
        """
        return self.state != StackState.NONE

    @property
    def id(self) -> str:
        return get_hash(self.name)

    def __repr__(self):
        """
        Stack repr
        """
        return f"<Stack: {self.name}>"

    def __eq__(self, other: "Stack") -> bool:
        """
        Check if Stack equal other Stack

        Args:
            other (Stack): Other Stack instance

        Returns:
            bool:
        """
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name
