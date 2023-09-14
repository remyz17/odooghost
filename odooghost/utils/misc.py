import hashlib


def labels_as_list(labels: dict[str, str]) -> list[str]:
    return [f"{k}={v}" for k, v in labels.items()]


def get_hash(data: str) -> str:
    return hashlib.md5(data.encode(), usedforsecurity=False).hexdigest()[:8]
