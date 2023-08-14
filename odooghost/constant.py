import pathlib

import typer

APP_DIR: pathlib.Path = pathlib.Path(
    typer.get_app_dir(app_name="odooghost", force_posix=True)
).resolve()
SRC_DIR: pathlib.Path = pathlib.Path(__file__).absolute().parent
LABEL_NAME: str = "odooghost"
LABEL_STACKNAME: str = f"{LABEL_NAME}_stackname"
LABEL_STACK_SERVICE_TYPE: str = f"{LABEL_NAME}_stack_type"
COMMON_NETWORK_NAME: str = f"{LABEL_NAME}_bridge"
