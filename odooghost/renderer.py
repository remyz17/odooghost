import typing as t

from jinja2 import Environment as JEnv
from jinja2 import FileSystemLoader

from odooghost import constant

env = JEnv(
    loader=FileSystemLoader((constant.SRC_DIR / "templates").as_posix()),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_dockerfile(
    odoo_version: str,
    apt_dependencies: t.Optional[t.List[str]] = None,
    pip_dependencies: t.Optional[t.List[str]] = None,
) -> str:
    """
    Render custom dockerfile for Odoo image

    Args:
        odoo_version (str): _description_
        apt_dependencies (t.Optional[t.List[str]], optional): Apt deps. Defaults to None.
        pip_dependencies (t.Optional[t.List[str]], optional): Python deps. Defaults to None.

    Returns:
        str: Rendered dockerfile
    """
    return env.get_template("Dockerfile.j2").render(
        odoo_version=odoo_version,
        apt_dependencies=apt_dependencies,
        pip_dependencies=pip_dependencies,
    )
