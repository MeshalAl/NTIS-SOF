import click


@click.group()
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    show_default=True,
    help="""disables caching,
              always fetches data from the source""",
)
@click.pass_context
def fetch(ctx, no_cache: bool):

    if no_cache:
        click.secho("Cache disabled", fg="blue")
        ctx.obj["config"].api.use_cache = False
        ctx.obj["api"] = StackOverflowAPI(ctx.obj["config"].api)
    else:
        ctx.obj["api"] = StackOverflowAPI(ctx.obj["config"].api)


@click.group()
@click.option(
    "--database-url",
    type=str,
    help="database url to connect to: defaults to .env DATABASE_URL",
    default=None,
    required=False,
)
@click.pass_context
def bookmark(ctx, database_url: str):

    ctx.obj["api"] = StackOverflowAPI(ctx.obj["config"].api)
    try:
        from db.database import DatabaseManager

        db_manager = DatabaseManager(database_url=database_url)
        db_manager.check_connection()
        ctx.obj["db_manager"] = db_manager
    except Exception as e:
        raise click.ClickException(f"Database connection failed: {e}")


@click.group()
@click.pass_context
def sof_file(ctx):
    from handlers.sof_filehandler import SOFFileHandler

    try:
        config = ctx.obj.get("config")

        handler = SOFFileHandler(config=config)
        ctx.obj["sof_handler"] = handler

    except Exception as e:
        raise click.ClickException(f"File handler failed: {e}")


from cli.sub_commands.bookmark_commands import *
from cli.sub_commands.fetch_commands import *
from cli.sub_commands.sof_file_commands import *
