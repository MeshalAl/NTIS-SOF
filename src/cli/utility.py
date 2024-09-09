import os
import sys
import json
from rich import table, console, print
from typing import Any
import codecs


def is_piped_out() -> bool:
    return not os.isatty(sys.stdout.fileno())

def is_piped_in() -> bool:
    return not os.isatty(sys.stdin.fileno())

def create_pipe_data(source, data) -> dict[str, Any]:
    return {"source": source, "data": data}


def serialize_to_stdout(pipe_data: dict[str, Any]) -> None:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='strict')
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