from click import pass_context, option, command, Choice
from api.stackoverflow_api import StackOverflowAPI
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from config.config_loader import Config, APIConfig, APIParams, RedisConfig, DBConfig
from models.sof_models import SOFUser
from pydantic import ValidationError
from cli.utility import is_piped, create_pipe_data, serialize_to_stdout


# TODO: find a clean way to make default param values dynamic
# for now default is hardcoded on the help message.
@command()
@option("--page", type=int, help="Page number to fetch, default: 1", required=False)
@option(
    "--pagesize",
    type=int,
    help="Number of users to fetch. default: 10",
    required=False,
)
@option("--filter", type=str, help="Filter to apply, default: filters ", required=False)
@option(
    "--order",
    type=Choice(["asc", "desc"]),
    help="Order to apply, default: desc",
    required=False,
)
@option(
    "--sort",
    type=Choice(["creation", "reputation", "name"]),
    help="Sort to apply, default: creation",
    required=False,
)
@option(
    "--display-columns",
    "-dc",
    multiple=True,
    default=["display_name", "user_id", "reputation", "last_access_date"],
    help="""Columns to display:
        usage: -cd display_name -dc user_id -dc reputation -dc last_access_date
        
        column must be a valid field in the user model:
        
        user_id: int
        account_id: int
        display_name: str
        user_age: int | None = None
        reputation: int
        location: str | None = None
        user_type: str
        last_access_date: int | None = None
        view_count: int | None = None
        question_count: int | None = None
        answer_count: int | None = None
        profile_image: str | None = None""",
    required=False,
)
@pass_context
def fetch_users(ctx, **kwargs):

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
        raise

    api = StackOverflowAPI().users
    users, meta = api.get_users(api_config.params)

    # make a dedicated rich table printer function

    if not is_piped():
        table = Table(title="Users", expand=True)

        unordered_columns: set = set(kwargs.get("display_columns"))
        if not unordered_columns.issubset(SOFUser.model_fields.keys()):
            raise ValueError(
                f"Invalid column name, must be one of {SOFUser.model_fields.keys()}"
            )

        ordered_columns: list = kwargs.get("display_columns")

        if users:
            try:
                table.add_column("#", style="white", no_wrap=True, justify="center")
                for column in ordered_columns:
                    table.add_column(
                        column, style="cyan", no_wrap=True, justify="center"
                    )

                for i, user in enumerate(users, start=1):
                    table.add_row(
                        str(i),
                        *[
                            str(user[column]) if column in user else "N/A"
                            for column in ordered_columns
                        ],
                    )
            except Exception as e:
                print(e)

            console = Console()

            if meta:
                metadata_str = " - ".join([f"{k}: {v}" for k, v in meta.items()])
                metadata_panel = Panel(
                    metadata_str, title="Meta", expand=True, style="white"
                )
                group = Group(table, metadata_panel)
                console.print(group)
            else:
                console.print(table)
    if is_piped():
        serialize_to_stdout(create_pipe_data("fetch_users", users))
