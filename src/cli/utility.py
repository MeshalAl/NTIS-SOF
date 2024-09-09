import os
import sys
import json
from rich import table, console, print
from typing import Any


def is_piped() -> bool:
    return not os.isatty(sys.stdout.fileno())


def create_pipe_data(source, data) -> dict[str, Any]:
    return {"source": source, "data": data}


def serialize_to_stdout(pipe_data: dict[str, Any]) -> None:
    json.dump(pipe_data, sys.stdout)
