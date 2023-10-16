import hashlib
import random
import string


def labels_as_list(labels: dict[str, str]) -> list[str]:
    return [f"{k}={v}" for k, v in labels.items()]


def get_hash(data: str) -> str:
    return hashlib.md5(data.encode(), usedforsecurity=False).hexdigest()[:8]


def get_random_string(length: int = 10) -> str:
    return "".join(
        random.choice(string.ascii_letters) for i in range(length)  # nosec B311
    )
