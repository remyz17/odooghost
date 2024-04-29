import typing as t
from pathlib import Path

import typer
from loguru import logger

from odooghost import exceptions
from odooghost.services import db, odoo
from odooghost.stack import Stack
from odooghost.utils import exec, misc
from odooghost.utils.autocomplete import ac_stacks_lists

if t.TYPE_CHECKING:
    from odooghost.container import Container

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def dump(
    stack_name: t.Annotated[
        str,
        typer.Argument(
            ..., help="Stack name", show_default=False, autocompletion=ac_stacks_lists
        ),
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
            "pg_dump exited with non 0 code, would you like to continue ?"
        ):
            raise typer.Abort()

        logger.debug("Transfering dump from container ...")
        now = misc.get_now()
        data, _ = db_container.get_archive(path=dump_path)
        dest_path = dest / f"{stack.name}_dump_db_{dbname}_{now}.tar"
        misc.write_tar(dest=dest_path, data=data)
        logger.info(f"Transfered dump file at {dest_path.as_posix()}")

        odoo_container = t.cast(
            "Container", stack.get_service(name="odoo").get_container()
        )
        filestore_path = odoo.get_filestore_path(dbname=dbname)
        if not exec.folder_exists(container=odoo_container, folder_path=filestore_path):
            logger.warning(f"Filestore at {filestore_path} doest not exists !")
            return

        logger.debug("Transfering filestore from container ...")
        data, _ = odoo_container.get_archive(path=filestore_path)
        dest_path = dest / f"{stack.name}_dump_filestore_{dbname}_{now}.tar"
        misc.write_tar(dest=dest_path, data=data)
        logger.info(f"Transfered filestore at {dest_path.as_posix()}")
        logger.info(f"Done dumping stack {stack_name} data !")
    except exceptions.StackException as err:
        logger.error(f"Failed to dump {stack_name} data !")
        logger.error(err)


@cli.command()
def restore(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name", autocompletion=ac_stacks_lists),
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
            dir_okay=True,
            readable=True,
            resolve_path=True,
            exists=True,
            help="Database filestore path",
        ),
    ] = None,
    jobs: t.Annotated[
        int,
        typer.Option(
            "-j",
            "--jobs",
            help="Postgres pg_restore jobs (Only availible in --pg-format=d)",
        ),
    ] = 4,
    force: t.Annotated[
        bool,
        typer.Option(
            "-f",
            "--force",
            help="Drop database if already exists",
        ),
    ] = False,
) -> None:
    """
    Restore database and/or filestore in Stack
    """
    if (
        filestore_path
        and filestore_path.is_file()
        and not misc.is_tarfile(filestore_path)
    ):
        logger.error(
            "Provide a valid filestore ! Either a folder or a tar(gz) archive."
        )
        raise typer.Abort()
    try:
        stack = Stack.from_name(name=stack_name)
        db_container = t.cast("Container", stack.get_service(name="db").get_container())

        if db.database_exsits(container=db_container, dbname=dbname):
            if not force:
                logger.error(f"Database {dbname} already exists !")
                raise typer.Abort()
            logger.info(f"Droping old database {dbname} ...")
            if db.drop_database(container=db_container, dbname=dbname) != 0:
                logger.error(f"Failed to drop database {dbname} !")
                raise typer.Abort()

        logger.info("Transfering dump to container ...")
        dest_dump_path = Path(
            f"/tmp/odooghost_restore_{dbname}_{misc.get_now()}"  # nosec B108
        )

        with misc.temp_tar_gz_file(dump_path) as tar_dump_path:
            if tar_dump_path is None:
                tar_dump_path = dump_path
            exec.create_folder(container=db_container, folder_path=dest_dump_path)
            with open(tar_dump_path, "rb") as stream:
                db_container.put_archive(path=dest_dump_path, data=stream)

        logger.info("Creating database ...")
        if db.create_database(container=db_container, dbname=dbname) != 0:
            logger.error(f"Failed to create database {dbname}!")
            raise typer.Abort()

        logger.info("Restoring dump ...")
        if db.restore_database(
            container=db_container,
            dbname=dbname,
            dump_path=dest_dump_path / dump_path.name,
            jobs=jobs,
        ) != 0 and not typer.confirm(
            "pg_restore exited with non 0 code, would you like to continue ?"
        ):
            logger.error("Failed to restore database !")
            raise typer.Abort()

        logger.info("Changing web base url ...")
        if db.change_base_url(container=db_container, dbname=dbname) != 0:
            logger.info(
                "The change web base url command return with non 0 code. Continuing..."
            )

        if filestore_path:
            odoo_container = t.cast(
                "Container", stack.get_service(name="odoo").get_container()
            )
            dest_filestore_path = odoo.get_filestore_path(dbname=dbname)
            if exec.folder_exists(
                container=odoo_container, folder_path=dest_filestore_path
            ):
                if not force:
                    logger.error("Filestore path already exists !")
                    raise typer.Abort()

                exec.remove_inode(
                    container=odoo_container, inode_path=dest_filestore_path
                )

            logger.info("Transfering filestore to container ...")
            with misc.temp_tar_gz_file(
                filestore_path, ignore_tar=True, include_root_dir=False
            ) as tar_filestore_path:
                if tar_filestore_path is None:
                    tar_filestore_path = filestore_path
                exec.create_folder(
                    container=odoo_container, folder_path=dest_filestore_path
                )
                with open(tar_filestore_path, "rb") as stream:
                    odoo_container.put_archive(path=dest_filestore_path, data=stream)

                exec.set_permissions(container=odoo_container, path=dest_filestore_path)

        logger.info(f"Done restoring stack {stack_name} data !")
    except exceptions.StackException as err:
        logger.error(f"Failed to restore {stack_name} data !")
        logger.error(err)


@cli.command()
def drop(
    stack_name: t.Annotated[
        str,
        typer.Argument(..., help="Stack name", autocompletion=ac_stacks_lists),
    ],
    dbname: t.Annotated[str, typer.Argument(help="Database name")],
) -> None:
    """
    Drop database and filestore from Stack
    """
    try:
        stack = Stack.from_name(name=stack_name)
        db_container = t.cast("Container", stack.get_service(name="db").get_container())

        if not db.database_exsits(container=db_container, dbname=dbname):
            logger.error(f"Database {dbname} doest not exists !")
            raise typer.Abort()

        logger.info("Dropping database ...")
        if db.drop_database(container=db_container, dbname=dbname) != 0:
            logger.error(f"Failed to drop database {dbname} !")
            raise typer.Abort()

        odoo_container = t.cast(
            "Container", stack.get_service(name="odoo").get_container()
        )
        logger.info("Removing filestore ...")
        if (
            exec.remove_inode(
                container=odoo_container,
                inode_path=odoo.get_filestore_path(dbname=dbname),
            )
            != 0
        ):
            logger.error(f"Failed to remove database {dbname} filestore !")
            raise typer.Abort()
        logger.info(f"Done restoring stack {stack_name} data !")
    except exceptions.StackException as err:
        logger.error(f"Failed to drop {stack_name} {dbname} !")
        logger.error(err)


@cli.callback()
def callback() -> None:
    """
    Data subcommands allow you to manage Odoo stacks data
    """
