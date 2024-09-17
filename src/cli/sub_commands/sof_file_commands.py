import click
from cli.commands import sof_file
from cli.utility import (
    is_piped_in,
    is_piped_out,
    create_pipe_data,
    get_users_from_pipe,
    user_pagination_prompt,
    deserialize_from_stdin,
    serialize_to_stdout,
)
from cli.options.sof_file_options import soffile_options
from ui.rich_builders import (
    build_rich_table,
    add_rich_row,
    add_rich_panel,
    build_rich_view,
)
from models.sof_models import SOFUser, SOFFile
from handlers.sof_filehandler import SOFFileHandler
from pydantic import ValidationError


@soffile_options
@sof_file.command()
@click.pass_context
def save(ctx, path: str | None):
    file_handler: SOFFileHandler = ctx.obj["sof_handler"]

    if not is_piped_in():
        raise click.UsageError("No data piped in, pipe data from fetch command")

    sof_users, meta = get_users_from_pipe("fetch", deserialize_from_stdin())

    file_handler.save(sof_users, meta, path)

    click.secho(
        f"Saved {len(sof_users)} users to {file_handler.resolved_path}", fg="green"
    )


@click.option(
    "--display-columns",
    "-dc",
    multiple=True,
    default=["display_name", "user_id", "reputation", "last_access_date"],
    help="""Columns to display:
        usage: -dc display_name -dc user_id -dc reputation -dc last_access_date
        
        valid columns:
        user_id
        account_id
        display_name
        user_age
        reputation
        location
        user_type
        last_access_date
        view_count
        question_count
        answer_count
        profile_image""",
    required=False,
)
@soffile_options
@sof_file.command()
@click.pass_context
def load(ctx, path: str | None, display_columns: list[str] | None) -> None:

    file_handler: SOFFileHandler = ctx.obj["sof_handler"]
    sof_file = file_handler.load(path)

    try:
        sof_users: list[SOFUser] = sof_file.users
        sof_meta: dict = sof_file.meta
    except ValidationError as e:
        raise click.ClickException(f"Deserialization failed: {e}")

    if not sof_users:
        raise ValueError("No users found in file")

    if not is_piped_out():
        unordered_columns: set = set(display_columns)  # type: ignore
        if not unordered_columns.issubset(SOFUser.model_fields.keys()):
            raise ValueError(
                f"Invalid column name, must be one of {SOFUser.model_fields.keys()}"
            )
        ordered_columns: tuple[str] = display_columns  # type: ignore

        table = build_rich_table(
            table_title="SOF File", display_columns=ordered_columns
        )

        panel = add_rich_panel(sof_meta, "SOF File Meta")

        add_rich_row(
            table=table,
            table_data=[user.model_dump() for user in sof_users],
            display_columns=ordered_columns,
        )
        build_rich_view([table, panel])
    else:
        all_users = [user.model_dump() for user in sof_users]

        pipe_data = {"users": all_users, "meta": sof_meta}
        serialize_to_stdout(create_pipe_data("sof_file", pipe_data))
