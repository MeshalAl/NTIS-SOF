from click import pass_context, option, command, Choice, echo
from api.stackoverflow_api import StackOverflowAPI
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from config.config_loader import Config, APIConfig, APIParams, RedisConfig
from models.sof_models import SOFUser
from models.bookmark_model import Bookmark
from pydantic import ValidationError
from cli.utility import is_piped_in, is_piped_out, create_pipe_data, serialize_to_stdout, deserialize_from_stdin


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
        raise e

    api = StackOverflowAPI().users
    users, meta = api.get_users(api_config.params)

    # TODO: make a dedicated rich table printer function

    if not is_piped_out():
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
    if is_piped_out():
        serialize_to_stdout(create_pipe_data("fetch_users", users))
@command()
@option("--user-id", "-id", multiple=True, help="specify the user ids", required=False)
@option("--remove-user", "-rm", is_flag=True, default=False, help="Operation to be executed on users", required=False)
@option("--add-user", "-add", is_flag=True, default=False, help="Operation to be executed on users", required=False)
@option("--page-size", "-ps", type=int, default=10,  help="number of users to display per page", required=False)
@option("--page", "-p", type=int, default=1, help="page number to display", required=False)
def bookmark(**kwargs):

    from db.database import get_session
    from db.dal.bookmark_dal import create_bookmark, get_bookmarks, delete_bookmark
    db = next(get_session())

    if is_piped_in():
        pipe_data = deserialize_from_stdin()
        
        if pipe_data.get("source") == "fetch_users":
            users: Bookmark = [Bookmark(**user) for user in pipe_data.get("data")]
        if not users:
            raise ValueError("Pipe does not contain any user data")
        
        # find current operation, add or remove

        if kwargs.get("add_user") and not kwargs.get("remove_user"):
            
            for user in users:
                create_bookmark(user, db)
                
            echo(f"{len(users)} users added to bookmarks", color=True)

        if kwargs.get("remove_user") and not kwargs.get("add_user"):

            for user in users:
                delete_bookmark(user.get("user_id"), db)

    elif not is_piped_out() and not kwargs.get("add_user") and not kwargs.get("remove_user"):
        pass
        
        
        # orm logic to fetch bookmarks based on page size. number later we figure it.
        
            


    # if no options are passed, then display the bookmarks
    # fetch bookmarks from db
    # display the bookmarks in a table
    # if no bookmarks found, display a message saying no bookmarks found.
    # if -d flag is passed, then delete the user by id, if no id is passed, then SEND A WARNING MESSAGE AND ASK FOR CONFIRMATION
# psudeo code for bookmarking
# two methods of data input, either get from pipe, or by fetching single user by id.
# if through pipe, then format and push it to orm. if by id, then fetch user and push to orm.
# to remove a user, either by id or by piped data.
# to view, just fetch them from db and display using the same table logic as fetch_users.

# WARNING: no mixing between the two modes, either by id or by pipe, not both, same goes with remove and view
# by default its viewing the bookmarks, with pagination.
# if no bookmarks, then display a message saying no bookmarks found.
# if -d flag is passed, then delete the user by id, if no id is passed, then SEND A WARNING MESSAGE AND ASK FOR CONFIRMATION
