import sys
import typing as t
from functools import reduce
from pathlib import Path

from docker.constants import DEFAULT_DATA_CHUNK_SIZE
from docker.models.containers import _create_container_args
from loguru import logger

from odooghost import constant
from odooghost.context import ctx
from odooghost.types import Attrs, Filters
from odooghost.utils import signals
from odooghost.utils.stream import split_buffer

if not constant.IS_WINDOWS_PLATFORM:
    from dockerpty.pty import ExecOperation, PseudoTerminal


def get_container_name(attrs: Attrs) -> str:
    if not attrs.get("Name") and not attrs.get("Names"):
        return None
    # inspect
    if "Name" in attrs:
        return attrs["Name"]
    # ps
    shortest_name = min(attrs["Names"], key=lambda n: len(n.split("/")))
    return shortest_name.split("/")[-1]


class Container:
    """
    Represents a Docker container
    """

    def __init__(self, attrs: Attrs, has_been_inspected: bool = False) -> None:
        self.client = ctx.docker.api
        self.attrs = attrs
        self.has_been_inspected = has_been_inspected

    @classmethod
    def from_ps(cls, attrs: Attrs, **kwargs) -> "Container":
        name = get_container_name(attrs)
        if name is None:
            return None

        new_attrs = {
            "Id": attrs["Id"],
            "Image": attrs["Image"],
            "Name": "/" + name,
        }
        return cls(new_attrs, **kwargs)

    @classmethod
    def from_id(cls, id) -> "Container":
        return cls(ctx.docker.api.inspect_container(id), has_been_inspected=True)

    @classmethod
    def create(cls, **options) -> "Container":
        options["version"] = ctx.docker.api._version
        create_kw = _create_container_args(options)
        response = ctx.docker.api.create_container(**create_kw)
        return cls.from_id(response["Id"])

    @classmethod
    def search(
        cls,
        filters: t.Optional[Filters] = None,
        stopped: bool = False,
    ) -> t.List["Container"]:
        return [
            cls.from_ps(container)
            for container in ctx.docker.api.containers(all=stopped, filters=filters)
        ]

    def reload(self) -> None:
        self.attrs = {}
        self.has_been_inspected = False

    def inspect(self) -> Attrs:
        self.attrs = self.client.inspect_container(self.id)
        self.has_been_inspected = True
        return self.attrs

    def inspect_if_not_inspected(self) -> None:
        if not self.has_been_inspected:
            self.inspect()

    def get(self, key: str) -> t.Any:
        self.inspect_if_not_inspected()

        def get_value(attrs, key) -> t.Any:
            return (attrs or {}).get(key)

        return reduce(get_value, key.split("."), self.attrs)

    def start(self, **options) -> None:
        return self.client.start(self.id, **options)

    def stop(self, **options) -> None:
        return self.client.stop(self.id, **options)

    def kill(self, **options) -> None:
        return self.client.kill(self.id, **options)

    def restart(self, **options) -> None:
        return self.client.restart(self.id, **options)

    def remove(self, **options) -> None:
        return self.client.remove_container(self.id, **options)

    def create_exec(self, command, **options):
        return self.client.exec_create(self.id, command, **options)

    def start_exec(self, exec_id, **options):
        return self.client.exec_start(exec_id, **options)

    def exec_run(
        self,
        command: t.List[str],
        stdout: bool = True,
        stderr: bool = True,
        stdin: bool = False,
        detach: bool = False,
        privileged: bool = False,
        user: t.Optional[str] = None,
        tty: bool = False,
        stream: bool = False,
        workdir: t.Optional[str] = None,
        pseudo_tty: bool = False,
    ) -> t.Tuple[t.Optional[int], t.Union[bytes, t.Generator, None]]:
        exec_id = self.create_exec(
            command,
            stdout=stdout,
            stderr=stderr,
            stdin=stdin,
            privileged=privileged,
            user=user,
            tty=tty,
            workdir=workdir,
        )
        if detach or not pseudo_tty:
            exec_output = self.start_exec(
                exec_id, tty=tty, stream=stream, detach=detach
            )
            if stream:
                return (None, exec_output)
            return (self.client.exec_inspect(exec_id).get("ExitCode"), exec_output)

        signals.set_signal_handler_to_shutdown()
        try:
            operation = ExecOperation(
                self.client,
                exec_id,
                interactive=tty,
            )
            pty = PseudoTerminal(self.client, operation)
            pty.start()
        except signals.ShutdownException:
            logger.info("received shutdown exception: closing")
        exit_code = self.client.exec_inspect(exec_id).get("ExitCode")
        return (exit_code, None)

    def wait(self):
        return self.client.wait(self.id).get("StatusCode", 127)

    def attach(self, *args, **kwargs):
        return self.client.attach(self.id, *args, **kwargs)

    def logs(self, *args, **kwargs):
        return self.client.logs(self.id, *args, **kwargs)

    def get_archive(
        self,
        path: str,
        chunk_size: int = DEFAULT_DATA_CHUNK_SIZE,
        encode_stream: bool = True,
    ) -> t.Tuple[t.Generator[any, any, None], t.Dict[str, t.Any]]:
        """
        _summary_

        Args:
            path (Path): Path to the file or folder to retrieve
            chunk_size (int, optional): The number of bytes returned by each iteration
                of the generator. If ``None``, data will be streamed as it is
                received. Defaults to 2 MB.
            encode_stream (bool, optional): Determines if data should be encoded
                (gzip-compressed) during transmission. Defaults to True.

        Returns:
            t.Tuple[t.Generator[any, any, None], t.Dict[str, t.Any]]:
                First element is a raw tar data stream. Second element is
                a dict containing ``stat`` information on the specified ``path``.
        """
        return self.client.get_archive(self.id, path, chunk_size, encode_stream)

    def put_archive(self, path: Path | str, data: bytes | t.IO) -> bool:
        """
        Insert a file or folder in this container using a tar archive as
        source.

        Args:
            path (Path | str): Path inside the container where the file(s) will be
                extracted. Must exist.
            data (bytes | t.IO): tar data to be extracted

        Returns:
            (bool): True if the call succeeds.
        """
        if isinstance(path, Path):
            path = path.as_posix()
        return self.client.put_archive(self.id, path, data)

    def get_local_port(self, port: int, protocol: t.Literal["tcp", "udp"] = "tcp"):
        port = self.ports.get(f"{port}/{protocol}")
        if port is None:
            return None
        port = port[0]
        host_ip, host_port = port.values()
        if constant.IS_DARWIN_PLARFORM and host_ip == "0.0.0.0":  # nosec B104
            host_ip = "localhost"
        return f"{host_ip}:{host_port}"

    def get_subnet_port(self, port: int) -> t.Optional[str]:
        subnet_ip = list(self.networks.values())[0].get("IPAddress", None)
        return f"{subnet_ip}:{port}" if subnet_ip else None

    def stream_logs(
        self,
        stream: t.IO = sys.stdout,
        tail: t.Optional[int] = None,
        follow: bool = True,
    ) -> None:
        for line in split_buffer(
            self.logs(stream=True, tail=tail or "all", follow=follow)
        ):
            stream.write(line)
            stream.flush()

    @property
    def id(self) -> str:
        return self.attrs["Id"]

    @property
    def image(self) -> str:
        return self.attrs["Image"]

    @property
    def image_config(self) -> dict:
        return self.client.inspect_image(self.image)

    @property
    def name(self) -> str:
        return self.attrs["Name"][1:]

    @property
    def stack(self) -> str:
        return self.labels.get(constant.LABEL_STACKNAME)

    @property
    def service(self) -> str:
        return self.labels.get(constant.LABEL_STACK_SERVICE_TYPE)

    @property
    def labels(self) -> dict[str, str]:
        return self.get("Config.Labels") or {}

    @property
    def ports(self) -> dict:
        return self.get("NetworkSettings.Ports") or {}

    @property
    def networks(self) -> dict:
        return self.get("NetworkSettings.Networks") or {}

    @property
    def stop_signal(self) -> t.Optional[str]:
        return self.get("Config.StopSignal")

    @property
    def exit_code(self) -> int:
        return self.get("State.ExitCode")

    @property
    def is_running(self) -> bool:
        return self.get("State.Running")

    @property
    def is_restarting(self) -> bool:
        return self.get("State.Restarting")

    @property
    def is_paused(self) -> bool:
        return self.get("State.Paused")

    @property
    def is_exited(self) -> bool:
        return self.get("State.Status") == "exited"

    def __repr__(self) -> str:
        return f"<Container: {self.name} ({self.id})>"

    def __eq__(self, other: "Container") -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> str:
        return self.id.__hash__()
