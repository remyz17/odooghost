import typing as t

if t.TYPE_CHECKING:
    from odooghost.container import Container


def folder_exists(container: "Container", folder_path: str) -> bool:
    _, res = container.exec_run(
        command=f"sh -c 'test -d {folder_path} && echo true || echo false'"
    )
    return True if "true" in res.decode() else False


def remove_inode(container: "Container", inode_path: str) -> bool:
    exit_code, _ = container.exec_run(command=f"rm -rf {inode_path}")
    return exit_code == 0


def create_folder(container: "Container", folder_path: str) -> bool:
    exit_code, _ = container.exec_run(command=f"mkdir -p {folder_path}")
    return exit_code == 0


def set_permissions(
    container: "Container", path: str, user: str = "odoo", group: str = "odoo"
):
    """
    Set permissions and ownership for a given path inside a Docker container.
    """
    exit_code, _ = container.exec_run(
        command=f"chown -R {user}:{group} {path}", user="root"
    )
    return exit_code == 0
