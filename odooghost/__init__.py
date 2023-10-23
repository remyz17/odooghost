import requests
import toml

"""
OdooGhost is a powerful tool tailored for streamlining the development and deployment of Odoo instances.
It offers an integrated solution that harnesses the power of Docker for orchestrating and managing these instances.
With both a Command Line Interface (CLI) and an upcoming web interface, managing Odoo stacks has never been simpler.
"""

__version__ = "0.2.1"


def check_version():
    res = requests.get(
        "https://raw.githubusercontent.com/remyz17/odooghost/main/pyproject.toml"
    )

    version = toml.loads(res.content.decode())["tool"]["poetry"]["version"]

    return (False, __version__) if version == __version__ else (True, version)
