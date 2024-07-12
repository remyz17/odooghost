import abc
import shutil
import sys
import typing as t
from contextlib import contextmanager
from pathlib import Path

from docker.errors import APIError, ImageNotFound, NotFound
from loguru import logger

from odooghost import constant, exceptions, utils
from odooghost.container import Container
from odooghost.context import ctx
from odooghost.filters import OneOffFilter
from odooghost.types import Filters, Labels
from odooghost.utils.misc import get_random_string, labels_as_list

if t.TYPE_CHECKING:
    from odooghost.config import StackConfig, StackServiceConfig


class BaseService(abc.ABC):
    def __init__(self, stack_config: "StackConfig") -> None:
        self.stack_config = stack_config
        self.stack_name = stack_config.name
        self._check_name_attribute()

    def _check_name_attribute(self):
        if not self.name:
            raise RuntimeError("The attribute name is required")

    def _prepare_build_context(self) -> None:
        """
        Prepare build context for service image build
        """
        logger.info(f"Preparing build context for {self.name}")
        self.build_context_path.mkdir(parents=True, exist_ok=True)

    def _clean_build_context(self) -> None:
        """
        Clean service image build context
        """
        shutil.rmtree(self.build_context_path.as_posix())

    @abc.abstractmethod
    def _get_environment(self) -> t.Dict[str, t.Any]:
        """
        Get service environment

        Returns:
            t.Dict[str, t.Any]: service environment
        """
        return {}

    def _get_ports_map(self) -> dict:
        """
        Get ports mapping
        Not that if service_port in config is None, a random port will be assigned

        Returns:
            dict: ports mapping
        """
        return {f"{self.container_port}/tcp": self.config.service_port}

    @abc.abstractmethod
    def _get_container_options(self, one_off: bool = False) -> t.Dict[str, t.Any]:
        return dict(
            name=self.container_name
            if not one_off
            else f"{self.container_name}_run_{get_random_string()}",
            image=self.image_tag if self.has_custom_image else self.base_image_tag,
            hostname=self.container_hostname,
            labels=self.labels(
                one_off=OneOffFilter.include if one_off else OneOffFilter.exclude
            ),
            environment=self._get_environment(),
            network=self.stack_config.get_network_name(),
            ports=self._get_ports_map() if not one_off else None,
        )

    def _do_pull(self, image_tag: str) -> str:
        logger.info(f"Pulling image {image_tag}")
        try:
            # TODO this should be moved
            all_events = list(
                utils.progress_stream.stream_output(
                    ctx.docker.api.pull(image_tag, stream=True),
                    sys.stdout,
                )
            )
        except exceptions.StreamOutputError:
            raise exceptions.StackImageBuildError(f"Failed to Pull {self.name}")

        return utils.progress_stream.get_digest_from_pull(events=all_events)

    def labels(self, one_off: OneOffFilter = OneOffFilter.exclude) -> Labels:
        """
        Get service labels

        Returns:
            Labels: Docker labels
        """
        labels = {
            constant.LABEL_NAME: "true",
            constant.LABEL_STACKNAME: self.stack_name,
            constant.LABEL_STACK_SERVICE_TYPE: self.name,
        }
        OneOffFilter.update_labels(value=one_off, labels=labels)
        return labels

    @contextmanager
    def build_context(self) -> None:
        """
        Build context contextmanager
        It ensure build context is cleaned event if an unknown error occurs
        """
        try:
            self._prepare_build_context()
            yield
        except Exception:
            raise
        finally:
            self._clean_build_context()

    def ensure_base_image(self, do_pull: bool = False) -> None:
        """
        Ensure service base image exists

        Args:
            do_pull (bool, optional): pull image. Defaults to False.

        Raises:
            exceptions.StackImagePullError: Error when pulling image
            exceptions.StackImageEnsureError: Error with docker client
        """
        logger.info(f"Ensuring image {self.base_image_tag}")
        try:
            ctx.docker.images.get(self.base_image_tag)
            if do_pull:
                self._do_pull(image_tag=self.base_image_tag)
        except ImageNotFound:
            try:
                self._do_pull(image_tag=self.base_image_tag)
            except APIError as err:
                raise exceptions.StackImagePullError(
                    f"Failed to pull image {self.base_image_tag}: {err}"
                )
        except APIError as err:
            raise exceptions.StackImageEnsureError(
                f"Failed to get image {self.base_image_tag}: {err}"
            )

    def build_image(
        self, path: Path, rm: bool = True, no_cache: bool = True, forcerm: bool = True
    ) -> str:
        """
        Build service image

        Args:
            path (Path): build context path
            rm (bool, optional): remove intermediate container. Defaults to True.
            no_cache (bool, optional): do not ser build cache. Defaults to True.

        Raises:
            exceptions.StackImageBuildError: When build fail

        Returns:
            str: image identifier
        """
        logger.info(f"Building {self.name} custom image")
        try:
            # TODO this should be moved
            all_events = list(
                utils.progress_stream.stream_output(
                    ctx.docker.api.build(
                        path=path.as_posix(),
                        tag=self.image_tag,
                        rm=rm,
                        forcerm=forcerm,
                        nocache=no_cache,
                        labels=self.labels(),
                    ),
                    sys.stdout,
                )
            )
        except exceptions.StreamOutputError:
            raise exceptions.StackImageBuildError(
                f"Failed to build {self.name} image, check dependencies"
            )

        image_id = utils.progress_stream.get_image_id_from_build(all_events)
        if image_id is None:
            raise exceptions.StackImageBuildError(
                f"Failed to build {self.name} image: {all_events[-1] if all_events else 'Unknown'}"
            )
        return image_id

    def drop_images(self) -> None:
        """
        Drop service image
        """
        images = [self.base_image_tag]
        if self.has_custom_image:
            images.insert(0, self.image_tag)
        for image_tag in images:
            try:
                ctx.docker.images.remove(image=image_tag)
            except NotFound:
                logger.warning(f"Image {image_tag} not found !")
            except APIError as err:
                logger.error(f"Failed to drop image {image_tag}: {err}")

    def create_volumes(self) -> None:
        """
        Create service volumes

        Raises:
            exceptions.StackVolumeCreateError: When volume creation fail
        """
        try:
            ctx.docker.volumes.create(
                name=self.volume_name,
                driver="local",
                labels=self.labels(),
            )
        except APIError as err:
            raise exceptions.StackVolumeCreateError(
                f"Failed to create {self.name} volume: {err}"
            )

    def drop_volumes(self) -> None:
        """
        Drop service volumes
        """
        try:
            volume = ctx.docker.volumes.get(self.volume_name)
            volume.remove()
        except NotFound:
            logger.warning(f"Volume {self.volume_name} not found !")
        except APIError as err:
            logger.error(f"Failed to drop volume {volume.id}: {err}")

    def containers(
        self,
        filters: t.Optional[Filters] = None,
        labels: t.Optional[Labels] = None,
        stopped: bool = True,
        one_off: OneOffFilter = OneOffFilter.exclude,
    ) -> t.List[Container]:
        """
        List service containers

        Args:
            filters (t.Optional[Filters], optional): filters. Defaults to None.
            labels (t.Optional[Labels], optional): docker lables. Defaults to None.
            stopped (bool, optional): stopped containers. Defaults to True.

        Returns:
            t.List[Container]: List of containers
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

    def create_container(self, one_off: bool = False, **options) -> Container:
        """
        Create service container

        Returns:
            Container: Container instance
        """
        default_options = self._get_container_options(one_off=one_off)
        default_options.update(options)
        return Container.create(**default_options)

    def drop_containers(self, all: bool = True, force: bool = True) -> None:
        """
        Drop service containers

        Args:
            all (bool, optional): Stopped containers. Defaults to True.
            force (bool, optional): Force remove. Defaults to True.
        """
        for container in self.containers(stopped=all):
            try:
                container.remove(force=force)
            except APIError as err:
                logger.error(f"Failed to drop container {container.id}: {err}")

    def get_container(self, raise_not_found: bool = True) -> Container:
        """
        Get service container

        Raises:
            exceptions.StackContainerNotFound: Container not found
            exceptions.StackContainerGetError: Docker client error

        Returns:
            Container: Container instance
        """
        try:
            return Container.from_id(id=self.container_name)
        except NotFound:
            if not raise_not_found:
                return None
            raise exceptions.StackContainerNotFound(
                f"Container {self.container_name} not found !"
            )
        except APIError as err:
            raise exceptions.StackContainerGetError(
                f"Failed to get container {self.container_name} : {err}"
            )

    def start_container(self) -> Container:
        """
        Start service container

        Raises:
            exceptions.StackContainerStartError: Start failed

        Returns:
            Container: Container instance
        """
        container = self.get_container()
        try:
            container.start()
            return container
        except APIError:
            raise exceptions.StackContainerStartError(
                f"Failed to start container {container.id}"
            )

    def build(self, rm: bool = True, no_cache: bool = True) -> None:
        """
        Build service

        Args:
            rm (bool, optional): remove intermediate containers. Defaults to True.
            no_cache (bool, optional): do not use build cache. Defaults to False.
        """
        if not self.has_custom_image:
            return None
        with self.build_context():
            self.build_image(path=self.build_context_path, rm=rm, no_cache=no_cache)

    def create(self, force: bool, do_pull: bool, **kw) -> None:
        """
        Create service

        Args:
            force (bool): force recreate dangling container
            do_pull (bool): pull base image
        """
        self.ensure_base_image(do_pull=do_pull)
        self.build()
        self.create_volumes()

        container = self.get_container(raise_not_found=False)
        if container is None:
            self.create_container()
            return

        if force:
            container.remove()
            self.create_container()
            return

        logger.warning(
            f"Service {self.name} container already created ! Use --force option to recreate."
        )

    def drop(self, volumes: bool = True, force: bool = False) -> None:
        """
        Drop service

        Args:
            volumes (bool, optional): drop service volumes. Defaults to True.
        """
        self.drop_containers()
        if volumes:
            self.drop_volumes()
        self.drop_images()

    def pull(self) -> None:
        """
        Pull service image
        """
        self._do_pull(image_tag=self.base_image_tag)

    def update(self) -> None:
        """
        Update service
        """
        self.build()
        self.drop_containers()
        self.create_container()

    @classmethod
    def list(cls, only_name: bool = False) -> list:
        all_services = cls.__subclasses__()
        if only_name:
            return [c.name for c in all_services]
        return all_services

    @abc.abstractproperty
    def config(self) -> t.Type["StackServiceConfig"]:
        """
        Get service config
        """
        return getattr(self.stack_config.services, self.name)

    @abc.abstractproperty
    def base_image_tag(self) -> str:
        """
        Base service image tag

        Returns:
            str: image tag
        """
        ...

    @property
    def image_tag(self) -> str:
        """
        Service image tag

        Returns:
            str: image tag
        """
        raise NotImplementedError()

    @abc.abstractproperty
    def has_custom_image(self) -> bool:
        """
        Service has custom image

        Returns:
            bool:
        """
        ...

    @property
    def volume_name(self) -> str:
        """
        Service volume name
        """
        return f"odooghost_{self.stack_name}_{self.name}_data"

    @property
    def container_name(self) -> str:
        """
        Service container name
        """
        return f"odooghost_{self.stack_name}_{self.name}"

    @abc.abstractproperty
    def container_port(self) -> int:
        """
        Service container port
        """
        ...

    @property
    def container_hostname(self) -> str:
        """
        Service container hostname
        """
        return self.stack_config.get_service_hostname(service=self.name)

    @property
    def build_context_path(self) -> Path:
        """
        Service build context path
        """
        return ctx.get_build_context_path() / self.stack_name / self.name
