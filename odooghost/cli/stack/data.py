import typing as t
from pathlib import Path

import typer
from loguru import logger

from odooghost import exceptions
from odooghost.services import db, odoo
from odooghost.stack import Stack
from odooghost.utils import exec, misc

if t.TYPE_CHECKING:
    from odooghost.container import Container

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def dump(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name", show_default=False),
    ],
    dbname: t.Annotated[str, typer.Argument(help="Database name", show_default=False)],
    dest: t.Annotated[
        Path,
        typer.Option(
            "-d",
            "--dest",
            file_okay=False,
            dir_okay=True,
            readable=True,
            writable=True,
            resolve_path=True,
            exists=True,
            help="Dump file(s) destination. Defaults to current directory",
        ),
    ] = Path("."),
    jobs: t.Annotated[
        int,
        typer.Option(
            "-j",
            "--jobs",
            help="Postgres pg_dump jobs (Only availible in --pg-format=d)",
        ),
    ] = 4,
    pg_format: t.Annotated[
        db.DumpFormat, typer.Option("--pg-format", help="Postgres dump format")
    ] = db.DumpFormat.d,
) -> None:
    """
    Dump one off Stack database and/or it's filestore.
    """
    try:
        stack = Stack.from_name(name=stack_name)
        db_container = t.cast("Container", stack.get_service(name="db").get_container())

        if not db.database_exsits(container=db_container, dbname=dbname):
            logger.error(f"Database {dbname} does not exists !")
            raise typer.Abort()

        logger.info(f"Dumping database {dbname} ...")
        exit_code, dump_path = db.dump_database(
            container=db_container, dbname=dbname, jobs=jobs, format=pg_format
        )
        if exit_code != 0 and not typer.confirm(
            "Database restore exited with non 0 code, would you like to continue ?"
        ):
            raise typer.Abort()

        logger.debug("Transfering dump from container ...")
        now = misc.get_now()
        data, _ = db_container.get_archive(path=dump_path)
        dest_path = dest / f"{stack.name}_dump_db_{dbname}_{now}.tar"
        misc.write_tar(dest=dest_path, data=data)
        logger.info(f"Writed dump file at {dest_path.as_posix()}")

        odoo_container = t.cast(
            "Container", stack.get_service(name="odoo").get_container()
        )
        filestore_path = odoo.get_filestore_path(dbname=dbname)
        if not exec.folder_exists(container=odoo_container, folder_path=filestore_path):
            logger.warning(f"Filestore at {filestore_path} doest not exists !")
            return
        logger.info("Dumping filestore ...")
        logger.debug("Transfering filestore from container ...")
        data, _ = odoo_container.get_archive(path=filestore_path)
        dest_path = dest / f"{stack.name}_dump_filestore_{dbname}_{now}.tar"
        misc.write_tar(dest=dest_path, data=data)
        logger.info(f"Writed filestore at {dest_path.as_posix()}")
        logger.info(f"Done dumping stack {stack_name} data !")
    except exceptions.StackException:
        pass


@cli.command()
def restore(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name"),
    ],
    dbname: t.Annotated[str, typer.Argument(help="Database name")],
    dump_path: t.Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=True,
            readable=True,
            resolve_path=True,
            exists=True,
            help="Database dump path",
        ),
    ],
    filestore_path: t.Annotated[
        t.Optional[Path],
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            exists=True,
            help="Database dump path",
        ),
    ] = None,
    jobs: t.Annotated[
        int, typer.Option("-j", "--jobs", help="Postgres pg_dump jobs")
    ] = 4,
) -> None:
    """
    Restore
    """
    try:
        pass
    except exceptions.StackException:
        pass


@cli.callback()
def callback() -> None:
    """
    Data subcommands allow you to manage Odoo stacks data
    """
