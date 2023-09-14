from jinja2 import Environment as JEnv
from jinja2 import FileSystemLoader

from odooghost import constant

env = JEnv(
    loader=FileSystemLoader((constant.SRC_DIR / "templates").as_posix()),
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=True,
)


def render_dockerfile(**kw) -> str:
    """
    Render custom dockerfile for Odoo image

    Returns:
        str: Rendered dockerfile
    """
    return env.get_template("Dockerfile.j2").render(**kw)
