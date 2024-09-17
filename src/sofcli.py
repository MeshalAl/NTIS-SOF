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
        raise click.FileError(f"Error loading config: {e.errors()}")

    ctx.obj["config"] = config



from cli import commands

start_cli.add_command(commands.fetch)
start_cli.add_command(commands.bookmark)
start_cli.add_command(commands.sof_file)
if __name__ == "__main__":

    try:
        start_cli()
    except Exception as e:
        click.echo(f"{e}", err=True, color=True, nl=True)

