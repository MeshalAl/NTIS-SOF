import os
import sys
import json
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from typing import Any
import codecs
import click
import keyboard
from time import sleep
from models.bookmark_model import Bookmark

def is_piped_out() -> bool:
    return not os.isatty(sys.stdout.fileno())


def is_piped_in() -> bool:
    return not os.isatty(sys.stdin.fileno())


def create_pipe_data(source, data) -> dict[str, Any]:
    return {"source": source, "data": data}


def serialize_to_stdout(pipe_data: dict[str, Any]) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="strict") # type: ignore
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


def user_pagination_prompt(page: int, input_delay: float = 0.25) -> int:
    
    escape_count = 0
    
    while True:
        click.echo(
            "Back: < | Next: > | Quit: q",
            nl=True,
            color=True,
        )
        event = keyboard.read_event(suppress=True)
        
        sleep(input_delay)
        if event.event_type == keyboard.KEY_DOWN:  # Only process key press events
            input = event.name
            click.echo() 
            match input:
                case "q":
                    if(click.confirm("Exit?", abort=False)):
                        exit(0)
                    continue
                case "right":
                    escape_count = 0 
                    return page + 1
                case "left":
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
                        click.clear()
                        exit(0)
                    escape_count += 1
                    click.secho(f"Invalid input, exiting in {3 -escape_count}", nl=True, fg="red")
                    continue

def get_users_from_pipe(source:str, pipe_data: dict[str, Any]) -> list[Bookmark]:

        if (
            pipe_data.get("source") == source
            and pipe_data.get("data") is not None
        ):
            piped_data = pipe_data.get("data")
            if piped_data is None or not isinstance(piped_data, list):
                raise ValueError("Invalid pipe data")
            
            users: list[Bookmark] = [Bookmark(**user) for user in piped_data] 
            return users
        else:
            raise ValueError("Invalid pipe data")