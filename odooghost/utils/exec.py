import typing as t

if t.TYPE_CHECKING:
    from odooghost.container import Container


def folder_exists(container: "Container", folder_path: str) -> bool:
    _, res = container.exec_run(
        command=f'test -d {folder_path} && echo "exists" || echo "not exists"'
    )
    return True if "exists" in res.decode() else False
