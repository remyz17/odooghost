from pathlib import Path
from pydantic import BaseModel
from odooghost.utils import plugins

plugins = plugins.Plugins()


class ContextConfig(BaseModel):
    """
    Context config holds configuration file
    """

    version: str
    """
    OdooGhost version
    """
    working_dir: Path
    """
    Working directory
    """


ContextConfig = plugins.configs(ContextConfig)
