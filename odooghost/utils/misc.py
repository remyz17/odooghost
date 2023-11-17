import hashlib
import random
import shutil
import string
import tarfile
import tempfile
import typing as t
from contextlib import contextmanager, suppress
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


def write_tar(dest: Path, data: t.Union[bytes, t.IO]) -> None:
    with open(dest.as_posix(), "wb") as stream:
        for chunk in data:
            stream.write(chunk)


def is_tarfile(filepath: t.Union[str, Path]) -> bool:
    if isinstance(filepath, str):
        filepath = Path(filepath)
    if not filepath.resolve().is_file():
        return False
    filepath = filepath.as_posix()
    with suppress(Exception):
        with open(filepath, "rb") as f:
            magic = f.read(2)
            if magic == b"\x1F\x8B":  # GZip magic bytes
                return True

        # If not gzip, check if it's a regular tar file
        if tarfile.is_tarfile(filepath):
            return True

        return False


@contextmanager
def temp_tar_gz_file(
    source_path: Path, ignore_tar: bool = False, include_root_dir: bool = True
) -> t.Generator[Path, None, None]:
    tempdir = tempfile.mkdtemp()
    tar_gz_path = Path(tempdir) / f"{source_path.name}.tar.gz"
    if is_tarfile(source_path) and not ignore_tar:
        tar_gz_path = source_path
    else:
        with tarfile.open(tar_gz_path, "w:gz") as tar:
            if include_root_dir or not source_path.is_dir():
                tar.add(source_path, arcname=source_path.name)
            else:
                for item in source_path.iterdir():
                    tar.add(item, arcname=item.name)
    try:
        yield tar_gz_path
    finally:
        if tar_gz_path != source_path:
            shutil.rmtree(tempdir)
