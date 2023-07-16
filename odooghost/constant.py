import pathlib

import typer

APP_DIR: pathlib.Path = pathlib.Path(
    typer.get_app_dir(app_name="odooghost", force_posix=True)
).resolve()
