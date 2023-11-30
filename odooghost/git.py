from pathlib import Path

from git import RemoteProgress, Repo
from loguru import logger
from rich import console, progress

from odooghost import exceptions


class GitRemoteProgress(RemoteProgress):
    OP_CODES = [
        "BEGIN",
        "CHECKING_OUT",
        "COMPRESSING",
        "COUNTING",
        "END",
        "FINDING_SOURCES",
        "RECEIVING",
        "RESOLVING",
        "WRITING",
    ]
    OP_CODE_MAP = {getattr(RemoteProgress, _op_code): _op_code for _op_code in OP_CODES}

    def __init__(self) -> None:
        super().__init__()
        self.progressbar = progress.Progress(
            progress.SpinnerColumn(),
            # *progress.Progress.get_default_columns(),
            progress.TextColumn("[progress.description]{task.description}"),
            progress.BarColumn(),
            progress.TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            "eta",
            progress.TimeRemainingColumn(),
            progress.TextColumn("{task.fields[message]}"),
            console=console.Console(),
            transient=False,
        )
        self.progressbar.start()
        self.active_task = None

    def __del__(self) -> None:
        # logger.info("Destroying bar...")
        self.progressbar.stop()

    @classmethod
    def get_curr_op(cls, op_code: int) -> str:
        """Get OP name from OP code."""
        # Remove BEGIN- and END-flag and get op name
        op_code_masked = op_code & cls.OP_MASK
        return cls.OP_CODE_MAP.get(op_code_masked, "?").title()

    def update(
        self,
        op_code: int,
        cur_count: str | float,
        max_count: str | float | None = None,
        message: str | None = "",
    ) -> None:
        # Start new bar on each BEGIN-flag
        if op_code & self.BEGIN:
            self.curr_op = self.get_curr_op(op_code)
            # logger.info("Next: %s", self.curr_op)
            self.active_task = self.progressbar.add_task(
                description=self.curr_op,
                total=max_count,
                message=message,
            )

        self.progressbar.update(
            task_id=self.active_task,
            completed=cur_count,
            message=message,
        )

        # End progress monitoring on each END-flag
        if op_code & self.END:
            # logger.info("Done: %s", self.curr_op)
            self.progressbar.update(
                task_id=self.active_task,
                message=f"[bright_black]{message}",
            )


class Git:
    @classmethod
    def clone(cls, path: Path, url: str, branch: str, depth: int = 1) -> Repo:
        logger.debug(f"Cloning {url} to {path} branch {branch} ...")
        try:
            return Repo.clone_from(
                url=url,
                to_path=path,
                branch=branch,
                progress=GitRemoteProgress(),
                depth=depth,
            )
        except Exception as err:
            raise exceptions.AddonsGitCloneError(
                f"Unknown exception during clone: {err}"
            )

    @classmethod
    def pull(
        cls, path: Path, branch: str, origin_name: str = "origin", depth: int = 1
    ) -> Repo:
        try:
            repo = Repo(path.as_posix())
            if not repo.git.status("--porcelain"):
                logger.debug(f"Pulling {path.as_posix()} branch {branch} ...")
                origin = repo.remote(name=origin_name)
                origin.pull(progress=GitRemoteProgress())
                return repo
            logger.warning("Skipping")
        except Exception as err:
            raise exceptions.AddonsGitCloneError(
                f"Unknown exception during clone: {err}"
            )
