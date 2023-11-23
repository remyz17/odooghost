from pathlib import Path

from git import RemoteProgress, Repo
from loguru import logger


class ProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=""):
        print(
            op_code,
            cur_count,
            max_count,
            cur_count / (max_count or 100.0),
        )


class Git:
    @classmethod
    def clone(cls, path: Path, url: str, branch: str, depth: int = 1) -> Repo:
        logger.info(f"Cloning {url} to {path} branch {branch} ...")
        try:
            return Repo.clone_from(
                url=url,
                to_path=path,
                branch=branch,
                progress=ProgressPrinter(),
                depth=depth,
            )
        except Exception as e:
            print(e)
            raise
