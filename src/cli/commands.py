from click import pass_context, option, command, Choice, echo, confirm
import click
from api.stackoverflow_api import StackOverflowAPI
from ui.rich_builders import build_rich_table
from config.config_loader import Config, APIConfig, APIParams, RedisConfig
from models.sof_models import SOFUser
from models.bookmark_model import Bookmark
from pydantic import ValidationError
from cli.utility import (
    is_piped_in,
    is_piped_out,
    create_pipe_data,
    serialize_to_stdout,
    deserialize_from_stdin,
    user_pagination_prompt,
)
from typing import List


# from cli.options import view, add, remove


# TODO: find a clean way to make default param values dynamic
# for now default is hardcoded on the help message.



@click.group()
@pass_context
def fetch(ctx, **kwargs):
    pass


@click.group()
@pass_context
def bookmark(ctx):
    pass


from cli.options import view, add, remove, users_by_id  # initalizing the commands
