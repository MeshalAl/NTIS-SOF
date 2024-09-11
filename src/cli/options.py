from sqlalchemy.orm import Session
from models.bookmark_model import Bookmark
from db.dal.bookmark_dal import create_bookmarks, delete_bookmarks, delete_all_bookmarks
import click
from cli.commands import fetch, bookmark
from typing import List, Tuple
from db.database import get_session
from cli.utility import (
    is_piped_in,
    is_piped_out,
    create_pipe_data,
    serialize_to_stdout,
    deserialize_from_stdin,
    user_pagination_prompt,
    get_users_from_pipe,
)
from ui.rich_builders import build_rich_table
from api.stackoverflow_api import StackOverflowAPI
from config.config_loader import APIConfig, byIDParams, APIParams
from models.sof_models import SOFUser
from pydantic import ValidationError

# type: ignore
@click.option(
    "--user-ids",
    "-id",
    multiple=True,
    type=int,
    help="specify the user ids",
    required=False,
)
@click.option(
    "--all",
    "-a",
    is_flag=True,
    default=False,
    help="Display all columns",
    required=False,
)
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
            case "fetch_users":
                users = get_users_from_pipe(source, pipe)
                with get_session() as session:
                    delete_bookmarks_option(session, users=users)
    elif user_ids:
        with get_session() as session:
            delete_bookmarks_option(session, user_ids=user_ids)
    elif all:
        with get_session() as session:
            nuke_bookmarks_option(session)
    else:
        raise click.UsageError("HOW DID YOU GET HERE?!")


@click.option(
    "--user-id",
    "-id",
    multiple=True,
    type=int,
    help="specify the user ids",
    required=False,
)
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
            case "fetch_users":
                users = get_users_from_pipe(source, pipe)
                with get_session() as session:
                    create_bookmarks_option(session, users=users)
        # TODO: add case for from file
    if user_id:
        sof_api = StackOverflowAPI()
        api_config: APIConfig = ctx.obj.get("config").api
        params = api_config.params

        by_id_params = byIDParams(site=params.site, filter=params.filter)
        with get_session() as db:
            create_bookmarks_option(
                db, user_ids=user_id, sof_api=sof_api, by_id_params=by_id_params
            )


@click.option(
    "--page-size",
    "-ps",
    type=int,
    default=10,
    help="number of users to display per page",
    required=False,
)
@click.option(
    "--page", "-p", type=int, default=1, help="page number to display", required=False
)
@click.option(
    "--display-columns",
    "-dc",
    multiple=True,
    default=["user_id", "display_name", "reputation", "last_access_date"],
    help="""Columns to display:
    default: user_id, display_name, reputation, last_access_date
    example: -dc user_id -dc display_name -dc reputation -dc last_access_date
    
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
@click.option(
    "--user-ids",
    "-id",
    multiple=True,
    type=int,
    help="specify the user ids",
    required=False, 
)
@bookmark.command()
@click.pass_context
def view(ctx, **kwargs):
    from db.database import get_session
    from db.dal.bookmark_dal import get_bookmarks

    unordered_columns: set = set(kwargs.get("display_columns")) # type: ignore
    if not unordered_columns.issubset(Bookmark.model_fields.keys()):
        raise ValueError(
            f"Invalid column name, must be one of {Bookmark.model_fields.keys()}"
        )
    ordered_columns: tuple[str] = kwargs.get("display_columns") # type: ignore

    pagination_flag = True
    while pagination_flag:
        if kwargs.get("user_ids"):
            with get_session() as db:
                results = get_bookmarks(
                    db,
                    page_size=kwargs.get("page_size"), # type: ignore
                    page=kwargs.get("page"), # type: ignore
                    user_ids=kwargs.get("user_ids"),
                )
        else:
            with get_session() as db:
                results = get_bookmarks(
                    db,
                    page_size=kwargs.get("page_size"), # type: ignore
                    page=kwargs.get("page"), # type: ignore
                )

        if not results:
            click.clear()
            click.secho("No pages to display", color=True, err=True, fg="yellow")
            user_input = user_pagination_prompt(kwargs.get("page")) # type: ignore
            kwargs["page"] = user_input
            continue

        results = [bookmark.model_dump() for bookmark in results]
        click.clear()
        build_rich_table(
            table_title="Bookmarks",
            table_data=results,
            display_columns=ordered_columns,
            add_panel=True,
            panel_data={"page": kwargs.get("page")},
        )

        user_input = user_pagination_prompt(kwargs.get("page")) # type: ignore
        kwargs["page"] = user_input


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
        
@click.option(
    "--display-columns",
    "-dc",
    multiple=True,
    default=["display_name", "user_id", "reputation", "last_access_date"],
    help="""Columns to display:
        usage: -cd display_name -dc user_id -dc reputation -dc last_access_date
        
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
@fetch.command()
@click.option("--user-id", "-id", multiple=True, type=int, help="specify the user ids", required=True)
@click.pass_context
def users_by_id(ctx, user_id: list[int], **kwargs):
    if not user_id:
        raise click.UsageError("No user ids provided")
    
    sof_api = StackOverflowAPI()
    api_config: APIConfig = ctx.obj.get("config").api
    params = api_config.params

    by_id_params = byIDParams(site=params.site, filter=params.filter)
    user_api = sof_api.users
    users = []
    for id in user_id:
        users_list, _ = user_api.get_user_by_id(id, by_id_params)
        users.extend([SOFUser(**user) for user in users_list])
    
        unordered_columns: set = set(kwargs.get("display_columns"))
        if not unordered_columns.issubset(SOFUser.model_fields.keys()):
            raise ValueError(
                f"Invalid column name, must be one of {SOFUser.model_fields.keys()}"
            )
        ordered_columns: list = kwargs.get("display_columns")
        
        build_rich_table(
            table_title="Results",
            table_data=users,
            display_columns=ordered_columns,
            add_panel=False
        )
@click.option("--page", type=int, help="Page number to fetch, default: 1", required=False)
@click.option(
    "--pagesize",
    type=int,
    help="Number of users to fetch. default: 10",
    required=False,
)
@click.option(
    "--page-range",
    "-pr",
    type=int,
    default=1,
    help="""Number of pages to fetch, default: 1
    example: --page-range 5, will fetch 5 pages of users data, starting from page 1, useful for piping""",
    required=False,
)
@click.option("--filter", type=str, help="Filter to apply, default: filters ", required=False)
@click.option(
    "--order",
    type=click.Choice(["asc", "desc"]),
    help="Order to apply, default: desc",
    required=False,
)
@click.option(
    "--sort",
    type=click.Choice(["creation", "reputation", "name"]),
    help="Sort to apply, default: creation",
    required=False,
)
@click.option(
    "--display-columns",
    "-dc",
    multiple=True,
    default=["display_name", "user_id", "reputation", "last_access_date"],
    help="""Columns to display:
        usage: -cd display_name -dc user_id -dc reputation -dc last_access_date
        
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

    api = StackOverflowAPI().users

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

            users, meta = api.get_users(api_config.params)

            build_rich_table(
                table_title="Users",
                table_data=users,
                display_columns=ordered_columns,
                add_panel=True,
                panel_data=meta,
            )

            has_next = meta.get("has_more", False)
            if not has_next:
                paginate_flag = False
                break

            user_input = user_pagination_prompt(api_config.params.page)
            if user_input == -2:
                paginate_flag = False
                break

            api_config.params.page = user_input
            print(api_config.params.page)

    if is_piped_out():
        all_users = []
        for page in range(1, kwargs.get("page_range") + 1):
            api_config.params.page = page
            users, _ = api.get_users(api_config.params)
            all_users.extend(users)
        serialize_to_stdout(create_pipe_data("fetch_users", all_users))

    
    
    