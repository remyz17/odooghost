import enum
import typing as t
from pathlib import Path

from docker.types import Mount
from loguru import logger

from odooghost import renderer
from odooghost.utils import misc

from .base import BaseService

if t.TYPE_CHECKING:
    from odooghost import config
    from odooghost.container import Container


class DumpFormat(str, enum.Enum):
    d = "d"
    c = "c"
    p = "p"
    t = "t"


def database_exsits(container: "Container", dbname: str) -> bool:
    _, res = container.exec_run(
        command=f"psql -U odoo -c \"SELECT 1 FROM pg_database WHERE datname='{dbname}';\" postgres",  # nosec B608
        user="postgres",
    )
    return True if "1" in res.decode() else False


def drop_database(container: "Container", dbname: str) -> int:
    exit_code, _ = container.exec_run(
        command=f"psql -U odoo -c \"select pg_terminate_backend(pid) from pg_stat_activity where pid <> pg_backend_pid() and datname = '{dbname}';\" -d postgres",  # nosec B608
        user="postgres",
    )
    exit_code, _ = container.exec_run(
        command=f"dropdb -U odoo {dbname}",
        user="postgres",
    )
    return exit_code


def create_database(
    container: "Container", dbname: str, template: str = "template1"
) -> int:
    exit_code, _ = container.exec_run(
        command=f"createdb -U odoo -T {template} {dbname}",
        user="postgres",
    )
    return exit_code


def dump_database(
    container: "Container",
    dbname: str,
    jobs: int = 4,
    format: DumpFormat = DumpFormat.d,
) -> tuple[int, str]:
    dump_path = f"/tmp/odooghost_dump_{dbname}_{misc.get_now()}"  # nosec B108
    if format == DumpFormat.p:
        dump_path += ".sql"
    elif format == DumpFormat.t:
        dump_path += ".tar"

    exit_code, data = container.exec_run(
        command=f"pg_dump -U odoo -F{format.value} {f'-j {jobs}' if format == DumpFormat.d else ''} -f {dump_path}  {dbname}",
        user="postgres",
    )
    if exit_code != 0:
        logger.warning(data.decode())
    return exit_code, dump_path


def restore_database(
    container: "Container", dbname: str, dump_path: Path, jobs: int = 0
) -> int:
    exit_code, res = container.exec_run(
        command=f"pg_restore -U odoo --dbname={dbname} {f'--jobs={jobs}' if jobs > 0 else None} {dump_path.as_posix()}"
        if dump_path.suffix != ".sql"
        else f"psql -U odoo --dbname={dbname} -f {dump_path.as_posix()}",
        user="root",
    )
    print(res.decode())
    return exit_code


def change_base_url(container: "Container", dbname: str) -> int:
    exit_code, _ = container.exec_run(
        command=f"psql -U odoo --dbname={dbname} --command=\"delete from ir_config_parameter where key = 'web.base.url.freeze';\"",
        user="root",
    )
    return exit_code


class DbService(BaseService):
    name = "db"

    def __init__(self, stack_config: "config.StackConfig") -> None:
        super().__init__(stack_config=stack_config)

    def _prepare_build_context(self) -> None:
        super()._prepare_build_context()
        with open((self.build_context_path / "Dockerfile").as_posix(), "w") as stream:
            logger.debug("Rendering Dockerfile for PostgreSQL with pgvector ...")
            stream.write(
                renderer.render_db_dockerfile(
                    postgres_version=self.config.version,
                )
            )

    def _get_environment(self) -> t.Dict[str, t.Any]:
        return dict(
            POSTGRES_DB=self.config.db,
            POSTGRES_USER=self.config.user or "odoo",
            POSTGRES_PASSWORD=self.config.password or "odoo",
        )

    def _get_container_options(self, one_off: bool = False) -> t.Dict[str, t.Any]:
        options = super()._get_container_options(one_off)
        target = (
            "/var/lib/postgresql"
            if self.config.version >= 18
            else "/var/lib/postgresql/data"
        )
        options.update(
            dict(
                mounts=[
                    Mount(
                        source=self.volume_name,
                        target=target,
                        type="volume",
                    )
                ],
            )
        )
        return options

    def ensure_base_image(self, do_pull: bool = False) -> None:
        if self.config.type == "remote":
            logger.warning("Skip postgres image as it's remote type")
        return super().ensure_base_image(do_pull)

    @property
    def config(self) -> "config.PostgresStackConfig":
        return super().config

    @property
    def is_remote(self) -> bool:
        return self.config.type == "remote"

    @property
    def base_image_tag(self) -> str:
        return f"{self.config.image or 'postgres'}:{self.config.version}"

    @property
    def image_tag(self) -> str:
        return f"odooghost_db_{self.stack_name}:postgres-{self.config.version}-pgvector".lower()

    @property
    def has_custom_image(self) -> bool:
        return True

    @property
    def container_port(self) -> int:
        return 5432
