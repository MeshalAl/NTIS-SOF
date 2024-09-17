import click
from typing import Any, Callable
from cli.utility import wrap_options


def soffile_options(func) -> Callable[..., Any]:
    options = [
        click.option(
            "--path",
            "-p",
            type=str,
            required=False,
            help="absolute path to the .SOF file: defaults to .env SOF_FILE_PATH if not provided or not absolute",
        ),
    ]
    return wrap_options(func, options=options)
