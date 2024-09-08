import click
from config.config_loader import load_config
from pathlib import Path
from pydantic import ValidationError


@click.group()
@click.option(
    "-cf",
    "--config-path",
    type=click.Path(exists=True),
    show_default=True,
    default=Path(__file__).parent / "config/defaults.yaml",
    help="Absolute path to the config file.",
    required=False,
)
@click.pass_context
def start_cli(ctx, config_path: str):
    ctx.ensure_object(dict)
    try:
        config = load_config(config_path)
    except ValidationError as e:
        raise click.FileError(f"Error loading config: {e.errors().messages}")

    ctx.obj['config'] = config

# importing so its hooked up as a registered command...
from cli import commands
start_cli.add_command(commands.fetch_users)

if __name__ == "__main__":

    try:
        start_cli()
    except Exception as e:
        click.echo(f"{e}", err=True, color=True, nl=True)
    
    

    # the flow branches into two main paths, one for regular command and argument based cli,
    # and the other for interactive
    # ex command based: python main.py -{function} -{args}, so fetch_users --page-size 10 --page 1
    # same goes on for bookmarking, ex python main.py bookmarks --add-user 293812 --add-user 293812,
    # adding users should also trigger writing to file? cache? db? all?? not sure yet.
    # python main.py bookmarks --remove-user 293812, maybe we can supply a list of ids to remove? would be nice
    # python main.py bookmarks --view-bookmarks, feels very straight forward, display the bookmarks. and thats it.
