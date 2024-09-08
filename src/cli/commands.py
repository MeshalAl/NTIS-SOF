from click import option, command, Choice
from api.stackoverflow_api import StackOverflowAPI
from rich.console import Console
from rich.table import Table
from config.config_loader import Config, APIConfig, APIParams, RedisConfig, DBConfig


# TODO: find a clean way to make default param values dynamic
# for now default is hardcoded on the help message.
@command()
@option("--page", type=int, help="Page number to fetch, default: 1", required=False)
@option("--page-size", type=int,
              help="Number of users to fetch. default: 10", required=False)
@option("--filter", type=str, help="Filter to apply, default: filters ", required=False)
@option("--order", type=Choice(["asc", "desc"]), help="Order to apply, default: desc", required=False)
@option("--sort", type=Choice(["creation", "reputation", "name"]), help="Sort to apply, default: creation", required=False)
def fetch_users(ctx, **kwargs):
    
    # explaination of whats going on here
    # we get the config (default values) from the context object, which has our pydantic model of the config.
    # then we update the config with the values passed in the command line, if any.
    # pydantic model will validate the values, and if they are not valid, it will raise an error.
    # if not then we good. we pass the config to the api, and fetch the users.

    api_config: APIConfig = ctx.obj.config.api    
    api_params : APIParams = api_config.params.model_copy(update=kwargs)

    api = StackOverflowAPI().users
    
    users = api.get_users(api_params)
    
    # make a dedicated rich table printer function
    table = Table(title="Users")
    if users:
        columns = users[0].keys()
        for column in columns:
            table.add_column(column, style="cyan", no_wrap=True)

        for user in users:
            table.add_row(*[str(user[column]) for column in columns])

    console = Console()
    console.print(table)