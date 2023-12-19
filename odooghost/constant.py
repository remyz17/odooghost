import enum
import pathlib
import sys

import typer

APP_DIR: pathlib.Path = pathlib.Path(
    typer.get_app_dir(app_name="odooghost", force_posix=True)
).resolve()
SRC_DIR: pathlib.Path = pathlib.Path(__file__).absolute().parent
STATIC_DIR: pathlib.Path = SRC_DIR / "web" / "dist"
LABEL_NAME: str = "odooghost"
LABEL_STACKNAME: str = f"{LABEL_NAME}_stackname"
LABEL_STACK_SERVICE_TYPE: str = f"{LABEL_NAME}_stack_type"
LABEL_ONE_OFF: str = f"{LABEL_NAME}_one_off"
COMMON_NETWORK_NAME: str = f"{LABEL_NAME}_bridge"
IS_WINDOWS_PLATFORM = sys.platform == "win32"
IS_DARWIN_PLARFORM = sys.platform == "darwin"
IS_LINUX_PLATFORM = sys.platform == "linux"

STACK_CONFIG_FILE_EXTENSIONS: list = ["yml", "yaml", "json"]


class OpenMode(str, enum.Enum):
    local = "local"
    subnet = "subnet"
