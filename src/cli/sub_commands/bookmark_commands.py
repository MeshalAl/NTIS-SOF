import click
from cli.commands import bookmark
from cli.utility import (
    deserialize_from_stdin,
    is_piped_in,
    get_users_from_pipe,
    user_pagination_prompt,
)
from db.dal.bookmark_dal import create_bookmarks, delete_bookmarks, delete_all_bookmarks
from models.bookmark_model import Bookmark
from models.sof_models import SOFUser
from sqlalchemy.orm import Session
from typing import Tuple, List, Any
from ui.rich_builders import (
    build_rich_table,
    add_rich_row,
    add_rich_panel,
    build_rich_view,
)
from api.stackoverflow_api import StackOverflowAPI
from config.config_loader import APIConfig, byIDParams
from cli.options.bookmark_options import add_options, view_options, remove_options


@view_options
@bookmark.command()
@click.pass_context
def view(ctx, **kwargs):
    from db.dal.bookmark_dal import get_bookmarks

    unordered_columns: set = set(kwargs.get("display_columns"))  # type: ignore
    if not unordered_columns.issubset(Bookmark.model_fields.keys()):
        raise ValueError(
            f"Invalid column name, must be one of {Bookmark.model_fields.keys()}"
        )
    ordered_columns: tuple[str] = kwargs.get("display_columns")  # type: ignore

    pagination_flag = True

    while pagination_flag:
        table = build_rich_table(
            table_title="Bookmarks", display_columns=ordered_columns
        )

        if kwargs.get("user_ids"):
            with ctx.obj["db_manager"].get_session() as db:
                results = get_bookmarks(
                    db,
                    page_size=kwargs.get("page_size"),  # type: ignore
                    page=kwargs.get("page"),  # type: ignore
                    user_ids=kwargs.get("user_ids"),
                )
        else:
            with ctx.obj["db_manager"].get_session() as db:
                results = get_bookmarks(
                    db,
                    page_size=kwargs.get("page_size"),  # type: ignore
                    page=kwargs.get("page"),  # type: ignore
                )

        if not results:
            click.clear()
            click.secho("No pages to display", color=True, err=True, fg="yellow")
            user_input = user_pagination_prompt(kwargs.get("page"))  # type: ignore
            kwargs["page"] = (
                user_input if kwargs["page"] > user_input else kwargs["page"]
            )
            continue
        else:
            results = [bookmark.model_dump() for bookmark in results]
            click.clear()

            panel = add_rich_panel(
                panel_data={"page": kwargs.get("page")}, title="Page Info"
            )
            add_rich_row(
                table=table, table_data=results, display_columns=ordered_columns
            )
            build_rich_view([table, panel])
        user_input = user_pagination_prompt(kwargs.get("page"))  # type: ignore
        kwargs["page"] = user_input


@remove_options
@bookmark.command()
@click.pass_context
def remove(ctx, user_ids: tuple[int], all: bool):

    if not (is_piped_in() or all or user_ids):
        raise click.UsageError(
            """Either pipe data from api or file, 
            or at least one user_id, or use --all flag"""
        )

    if sum([bool(is_piped_in()), bool(user_ids), bool(all)]) != 1:
        raise click.UsageError("multiple data sources, use only one option")

    if is_piped_in():
        pipe = deserialize_from_stdin()
        source = pipe.get("source")
        match source:
            case "fetch":
                users, _ = get_users_from_pipe(source, pipe)
                bookmark_users = [Bookmark.model_validate(user) for user in users]
                with ctx.obj["db_manager"].get_session() as session:
                    delete_bookmarks_option(session, users=bookmark_users)
            case "sof_file":
                users, _ = get_users_from_pipe(source, pipe)
                bookmark_users = [Bookmark.model_validate(user) for user in users]
                with ctx.obj["db_manager"].get_session() as session:
                    delete_bookmarks_option(session, users=bookmark_users)
            case _:
                click.secho("data source unknown", err=True, color=True, fg="red")
    elif user_ids:
        with ctx.obj["db_manager"].get_session() as session:
            delete_bookmarks_option(session, user_ids=user_ids)
    elif all:
        with ctx.obj["db_manager"].get_session() as session:
            nuke_bookmarks_option(session)
    else:
        raise click.UsageError("HOW DID YOU GET HERE?!")


@add_options
@bookmark.command()
@click.pass_context
def add(ctx, user_id: list[int]):
    if not (is_piped_in() or user_id):
        raise click.UsageError(
            """Either pipe data from api or file, 
            or at least one user_id"""
        )

    if sum([bool(is_piped_in()), bool(user_id)]) != 1:
        raise click.UsageError("multiple data sources, use only one option")

    if is_piped_in():
        pipe = deserialize_from_stdin()
        source = pipe.get("source")
        match source:
            case "fetch":
                users, _ = get_users_from_pipe(source, pipe)
                bookmark_users = [Bookmark(**user.model_dump()) for user in users]
                with ctx.obj["db_manager"].get_session() as session:
                    create_bookmarks_option(session, users=bookmark_users)
            case "sof_file":
                users, _ = get_users_from_pipe(source, pipe)
                bookmark_users = [Bookmark(**user.model_dump()) for user in users]
                with ctx.obj["db_manager"].get_session() as session:
                    create_bookmarks_option(session, users=bookmark_users)
            case _:
                click.secho("data source unknown", err=True, color=True, fg="red")

    if user_id:
        sof_api = ctx.obj.get("api")
        api_config: APIConfig = ctx.obj.get("config").api
        params = api_config.params

        by_id_params = byIDParams(site=params.site, filter=params.filter)
        with ctx.obj["db_manager"].get_session() as db:
            create_bookmarks_option(
                db, user_ids=user_id, sof_api=sof_api, by_id_params=by_id_params
            )


def create_bookmarks_option(
    db: Session,
    users: list[Bookmark] | None = None,
    user_ids: list[int] | None = None,
    sof_api: StackOverflowAPI | None = None,
    by_id_params: byIDParams | None = None,
):
    try:
        if user_ids and not users:
            if sof_api and by_id_params:
                user_api = sof_api.users
                bookmarks = []
                for user_id in user_ids:
                    users_list, _ = user_api.get_user_by_id(user_id, by_id_params)
                    bookmarks.extend([Bookmark(**user) for user in users_list])
                try:
                    create_bookmarks(db, bookmark=bookmarks)
                except ValueError as e:
                    raise e
        elif users and not user_ids:
            create_bookmarks(db, bookmark=users)
    except ValueError as e:
        click.secho(f"{e}", err=True, color=True, fg="red")


def delete_bookmarks_option(
    db: Session, users: list[Bookmark] | None = None, user_ids: Tuple[int] | None = None
):
    try:
        delete_bookmarks(session=db, bookmarks=users, user_ids=user_ids)
    except ValueError as e:
        click.secho(f"{e}", err=True, color=True, fg="red")


def nuke_bookmarks_option(db: Session):
    try:
        warning_prompt = click.confirm("Delete everything?", abort=True)
        if warning_prompt:
            delete_all_bookmarks(db)
        else:
            click.secho("nuke launch aborted", fg="yellow")
    except ValueError as e:
        click.secho(f"{e}", err=True, color=True, fg="red")
