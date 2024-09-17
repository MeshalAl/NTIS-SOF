import click
from cli.commands import fetch
from cli.utility import (
    is_piped_out,
    create_pipe_data,
    serialize_to_stdout,
    user_pagination_prompt,
)
from ui.rich_builders import (
    build_rich_table,
    add_rich_row,
    add_rich_panel,
    build_rich_view,
)
from api.stackoverflow_api import StackOverflowAPI
from config.config_loader import APIConfig, byIDParams, APIParams
from models.sof_models import SOFUser
from pydantic import ValidationError
from cli.options.fetch_options import by_id_options, bulk_options


@by_id_options
@fetch.command()
@click.pass_context
def users_by_id(ctx, user_id: list[int], **kwargs):
    if not user_id:
        raise click.UsageError("No user ids provided")

    sof_api = ctx.obj.get("api")
    api_config: APIConfig = ctx.obj.get("config").api
    params = api_config.params

    by_id_params = byIDParams(site=params.site, filter=params.filter)
    user_api = sof_api.users
    users = []
    for id in user_id:
        users_list, _ = user_api.get_user_by_id(id, by_id_params)
        users.extend([user for user in users_list])

    if not is_piped_out():
        unordered_columns: set = set(kwargs.get("display_columns"))
        if not unordered_columns.issubset(SOFUser.model_fields.keys()):
            raise ValueError(
                f"Invalid column name, must be one of {SOFUser.model_fields.keys()}"
            )
        ordered_columns: tuple[str] = kwargs.get("display_columns")

        table = build_rich_table(table_title="Results", display_columns=ordered_columns)
        panel = add_rich_panel(title="Param", panel_data=by_id_params.model_dump())

        add_rich_row(table=table, table_data=users, display_columns=ordered_columns)

        build_rich_view([table, panel])

    if is_piped_out():

        pipe_data = {"users": users, "meta": by_id_params.model_dump()}
        serialize_to_stdout(create_pipe_data("fetch", pipe_data))


@bulk_options
@fetch.command()
@click.pass_context
def users_bulk(ctx, **kwargs):
    api_config: APIConfig = ctx.obj.get("config").api
    api_params_fields = APIParams.model_fields.keys()
    # make it into util?

    user_options = {
        key: val
        for key, val in kwargs.items()
        if key in api_params_fields and val is not None
    }
    try:
        params = api_config.params.model_dump()
        params.update(user_options)
        validated_params = APIParams.model_validate(params)
        api_config.params = validated_params

    except ValidationError as e:
        raise e

    api: StackOverflowAPI.Users = ctx.obj.get("api").users

    # TODO: make a dedicated rich table printer function, done
    if not is_piped_out():

        unordered_columns: set = set(kwargs.get("display_columns"))
        if not unordered_columns.issubset(SOFUser.model_fields.keys()):
            raise ValueError(
                f"Invalid column name, must be one of {SOFUser.model_fields.keys()}"
            )
        ordered_columns: list = kwargs.get("display_columns")

        paginate_flag = True

        while paginate_flag:

            table = build_rich_table(
                table_title="Results", display_columns=ordered_columns
            )

            users, meta = api.get_users(api_config.params)

            panel = add_rich_panel(panel_data=meta, title="Meta")

            add_rich_row(table=table, table_data=users, display_columns=ordered_columns)
            build_rich_view([table, panel])

            has_next = meta.get("has_more", False)
            if not has_next:
                paginate_flag = False
                break

            user_input = user_pagination_prompt(api_config.params.page, max_depth=24)
            if user_input == -2:
                paginate_flag = False
                break

            api_config.params.page = user_input

    if is_piped_out():
        all_users = []

        for page in range(1, kwargs.get("page_range") + 1):
            api_config.params.page = page
            users, _ = api.get_users(api_config.params)
            all_users.extend(users)

        pipe_data = {"users": all_users, "meta": api_config.params.model_dump()}
        serialize_to_stdout(create_pipe_data("fetch", pipe_data))
