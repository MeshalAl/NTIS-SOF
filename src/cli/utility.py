import os
import sys
import json
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from typing import Any, Callable
import codecs
import click
import readchar
from time import sleep
from models.sof_models import SOFUser
import stat


def is_piped_out() -> bool:
    """Check if stdout is piped. source | target"""
    return not os.isatty(sys.stdout.fileno())


def is_piped_in() -> bool:
    """Check if stdin is piped, target | destination"""
    return not os.isatty(sys.stdin.fileno())


def create_pipe_data(source, data) -> dict[str, Any]:
    return {"source": source, "data": data}


def serialize_to_stdout(pipe_data: dict[str, Any]) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="strict")  # type: ignore
        json.dump(pipe_data, sys.stdout, ensure_ascii=False)
        sys.stdout.flush()
    except Exception as e:
        raise e


def deserialize_from_stdin() -> dict[str, Any]:
    try:
        # without this BOM character breaks the json load...
        reader = codecs.getreader("utf-8-sig")(sys.stdin.buffer)
        return json.load(reader)
    except Exception as e:
        raise e


def user_pagination_prompt(
    page: int, max_depth: int | None = None, input_delay: float = 0.1
) -> int:

    escape_count = 0

    while True:
        click.echo(
            "Back: < | Next: > | Quit: q",
            nl=True,
            color=True,
        )
        input_key = readchar.readkey()

        sleep(input_delay)

        match input_key:
            case "q":
                click.clear()
                if click.confirm("Exit?", abort=False):
                    exit(0)
                continue
            case readchar.key.RIGHT:
                escape_count = 0
                if max_depth and page > max_depth:
                    click.clear()
                    click.secho(
                        "Max depth reached, further pages require a token",
                        err=True,
                        nl=True,
                        fg="yellow",
                    )
                    continue
                return page + 1
            case readchar.key.LEFT:
                if page <= 1:
                    click.clear()
                    click.echo("You are on the first page", err=True, nl=True)
                    escape_count = 0
                    continue
                return page - 1
            case _:
                click.clear()
                if escape_count == 2:
                    click.echo("Exiting...", err=True, nl=True)
                    exit(0)
                escape_count += 1
                click.secho(
                    f"Invalid input, exiting in {3 -escape_count}",
                    nl=True,
                    fg="red",
                )
                continue


def get_users_from_pipe(
    source: str, pipe_data: dict[str, Any]
) -> tuple[list[SOFUser], dict[str, Any]]:
    # why did i make this bookmark specific?.. TODO: make it generic
    if pipe_data.get("source") == source and pipe_data.get("data") is not None:
        piped_data: dict = pipe_data.get("data")  # type: ignore
        piped_users = piped_data.get("users")

        if piped_users is None or not isinstance(piped_users, list):
            raise ValueError("Invalid pipe data")
        users: list[SOFUser] = [SOFUser(**user) for user in piped_users]
        meta: dict[str, Any] = piped_data.get("meta")

        return users, meta
    else:
        raise ValueError("Invalid or empty pipe data")


def wrap_options(func: Callable, options: list[Callable]) -> Callable:
    for option in options:
        func = option(func)
    return func
