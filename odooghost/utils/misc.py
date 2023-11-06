import hashlib
import random
import shutil
import string
import tarfile
import tempfile
import typing as t
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


def labels_as_list(labels: dict[str, str]) -> list[str]:
    return [f"{k}={v}" for k, v in labels.items()]


def get_hash(data: str) -> str:
    return hashlib.md5(data.encode(), usedforsecurity=False).hexdigest()[:8]


def get_random_string(length: int = 10) -> str:
    return "".join(
        random.choice(string.ascii_letters) for i in range(length)  # nosec B311
    )


def get_now() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


@contextmanager
def temp_tar_gz_file(source_path: Path, tar_name: str) -> t.Generator[Path, None, None]:
    tempdir = tempfile.mkdtemp()
    tar_gz_path = Path(tempdir) / f"{tar_name}.tar.gz"

    if source_path.is_dir() or not tarfile.is_tarfile(source_path):
        with tarfile.open(tar_gz_path, "w:gz") as tar:
            tar.add(source_path, arcname=source_path.name)
    else:
        tar_gz_path = source_path

    try:
        yield tar_gz_path
    finally:
        if tar_gz_path != source_path:
            shutil.rmtree(tempdir)


def write_tar(dest: Path, data: t.Union[bytes, t.IO]) -> None:
    with open(dest.as_posix(), "wb") as stream:
        for chunk in data:
            stream.write(chunk)
