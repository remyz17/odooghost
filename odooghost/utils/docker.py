import sys
import typing as t

from odooghost.container import Container

from .stream import split_buffer


def labels_as_list(labels: dict[str, str]) -> list[str]:
    return [f"{k}={v}" for k, v in labels.items()]


def stream_container_logs(container: Container, stream: t.IO = sys.stdout) -> None:
    for line in split_buffer(container.logs(stream=True, tail=0, follow=True)):
        stream.write(line)
        stream.flush()
