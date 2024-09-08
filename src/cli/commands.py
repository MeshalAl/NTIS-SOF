from click import pass_context, option, command, Choice
from api.stackoverflow_api import StackOverflowAPI
from rich.console import Console
from rich.table import Table
from config.config_loader import Config, APIConfig, APIParams, RedisConfig, DBConfig
from models.sof_models import SOFUser


# TODO: find a clean way to make default param values dynamic
# for now default is hardcoded on the help message.
@command()
@option("--page", type=int, help="Page number to fetch, default: 1", required=False)
@option(
    "--page-size",
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
@pass_context
def fetch_users(ctx, **kwargs):

    # explaination of whats going on here
    # we get the config (default values) from the context object, which has our pydantic model of the config.
    # then we update the config with the values passed in the command line, if any.
    # pydantic model will validate the values, and if they are not valid, it will raise an error.
    # if not then we good. we pass the config to the api, and fetch the users.

    api_config: APIConfig = ctx.obj.get("config").api
    
    # make it into util?
    to_update = {key:val for key, val in kwargs.items() if val is not None}
    
    api_params: APIParams = api_config.params.model_copy(update=to_update)

    api = StackOverflowAPI().users

    users, meta = api.get_users(api_params)

    # make a dedicated rich table printer function
    table = Table(title="Users")
    columns = SOFUser.model_fields.keys()
    if users:
        try:
            for column in columns:
                table.add_column(column, style="cyan", no_wrap=True)

            if users:
                for user in users:
                    table.add_row(*[str(user[column]) if column in user else "N/A" for column in columns])
        except Exception as e:
            print(e)
            
    console = Console()
    console.print(table)
