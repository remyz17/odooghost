import typing as t

import typer
from loguru import logger

from odooghost import exceptions
from odooghost.services import db
from odooghost.stack import Stack
from odooghost.utils.autocomplete import ac_stacks_lists

if t.TYPE_CHECKING:
    from odooghost.container import Container

cli = typer.Typer(no_args_is_help=True)

StackName = t.Annotated[
    str,
    typer.Argument(..., help="Stack name", autocompletion=ac_stacks_lists),
]
DbName = t.Annotated[
    str,
    typer.Argument(..., help="Database name", show_default=False),
]
Force = t.Annotated[
    bool,
    typer.Option("-y", "--yes", help="Do not ask for confirmation"),
]


def _get_db_container(stack_name: str, dbname: str) -> t.Tuple["Container", bool]:
    stack = Stack.from_name(name=stack_name)
    db_container = t.cast("Container", stack.get_service(name="db").get_container())
    started = False
    if not db_container.is_running:
        db_container.start()
        started = True
    if not db.database_exsits(container=db_container, dbname=dbname):
        logger.error(f"Database {dbname} does not exists !")
        raise typer.Abort()
    return db_container, started


def _run_db_tool(
    stack_name: str,
    dbname: str,
    message: str,
    func: t.Callable[..., t.Tuple[int, bytes]],
    force: bool,
    confirm_message: str,
    **kwargs: t.Any,
) -> None:
    if not force and not typer.confirm(confirm_message):
        raise typer.Abort()
    try:
        db_container, started = _get_db_container(stack_name, dbname)
        logger.info(message)
        exit_code, res = func(container=db_container, dbname=dbname, **kwargs)
        if exit_code != 0:
            logger.error(res.decode() if res else "Operation failed")
            raise typer.Abort()
        logger.info("Done !")
        if started:
            db_container.stop()
    except exceptions.StackException as err:
        logger.error(err)
        raise typer.Exit(code=1)


@cli.command()
def neutralize(
    stack_name: StackName,
    dbname: DbName,
    force: Force = False,
) -> None:
    """
    Neutralize a database (disable crons, mail servers and payment providers)
    """
    _run_db_tool(
        stack_name=stack_name,
        dbname=dbname,
        message=f"Neutralizing database {dbname} ...",
        func=db.neutralize_database,
        force=force,
        confirm_message=(
            f"This will disable crons, mail/fetchmail servers and payment "
            f"providers on database {dbname}. Continue ?"
        ),
    )


@cli.command(name="change-passwords")
def change_passwords(
    stack_name: StackName,
    dbname: DbName,
    force: Force = False,
) -> None:
    """
    Set every active user password to their login
    """
    _run_db_tool(
        stack_name=stack_name,
        dbname=dbname,
        message=f"Setting user passwords to their login on {dbname} ...",
        func=db.set_passwords_to_login,
        force=force,
        confirm_message=(
            f"This will set every active user password to their login on "
            f"database {dbname}. Continue ?"
        ),
    )


@cli.command(name="disable-2fa")
def disable_2fa(
    stack_name: StackName,
    dbname: DbName,
    force: Force = False,
) -> None:
    """
    Disable two-factor authentication (TOTP) for all users
    """
    _run_db_tool(
        stack_name=stack_name,
        dbname=dbname,
        message=f"Disabling two-factor authentication on {dbname} ...",
        func=db.disable_2fa,
        force=force,
        confirm_message=(
            f"This will disable two-factor authentication for all users on "
            f"database {dbname}. Continue ?"
        ),
    )


@cli.command(name="set-admin")
def set_admin(
    stack_name: StackName,
    dbname: DbName,
    login: t.Annotated[
        str, typer.Option("--login", help="New admin login")
    ] = "admin",
    password: t.Annotated[
        str, typer.Option("--password", help="New admin password")
    ] = "admin",
    force: Force = False,
) -> None:
    """
    Reset the admin user (id 2) credentials, defaults to admin:admin
    """
    _run_db_tool(
        stack_name=stack_name,
        dbname=dbname,
        message=f"Setting admin credentials to {login}:{password} on {dbname} ...",
        func=db.reset_admin_credentials,
        force=force,
        confirm_message=(
            f"This will reset the admin user credentials on database {dbname}. "
            f"Continue ?"
        ),
        login=login,
        password=password,
    )


@cli.command()
def anonymize(
    stack_name: StackName,
    dbname: DbName,
    force: Force = False,
) -> None:
    """
    Anonymize partners personal data (emails, phones and mobiles)
    """
    _run_db_tool(
        stack_name=stack_name,
        dbname=dbname,
        message=f"Anonymizing personal data on {dbname} ...",
        func=db.anonymize_database,
        force=force,
        confirm_message=(
            f"This will anonymize partners emails, phones and mobiles on "
            f"database {dbname}. Continue ?"
        ),
    )


@cli.callback()
def callback() -> None:
    """
    Database maintenance tools (neutralize, anonymize, credentials ...)
    """
