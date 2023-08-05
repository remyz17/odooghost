import pathlib

import typer

APP_DIR: pathlib.Path = pathlib.Path(
    typer.get_app_dir(app_name="odooghost", force_posix=True)
).resolve()
SRC_DIR: pathlib.Path = pathlib.Path(__file__).absolute().parent
LABEL_STACKNAME: str = "odooghost_stackname"
