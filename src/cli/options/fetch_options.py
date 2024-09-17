import click
from typing import Any, Callable
from cli.utility import wrap_options


def by_id_options(func: Callable) -> Callable[..., Any]:
    options = [
        click.option(
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
        ),
        click.option(
            "--user-id",
            "-id",
            multiple=True,
            type=int,
            help="specify the user ids",
            required=True,
        ),
    ]

    return wrap_options(func, options=options)


def bulk_options(func: Callable) -> Callable[..., Any]:
    options = [
        click.option(
            "--page",
            "-p",
            type=click.IntRange(1, 24),
            help="Page number to fetch, max page is 24 since it requires token for beyond, default: 1",
            required=False,
        ),
        click.option(
            "--pagesize",
            "-ps",
            type=int,
            help="Number of users to fetch. default: 10",
            required=False,
        ),
        click.option(
            "--page-range",
            "-pr",
            type=int,
            default=1,
            help="""Number of pages to fetch, default: 1
    example: --page-range 5, will fetch 5 pages of users data, starting from page 1, useful for piping""",
            required=False,
        ),
        click.option(
            "--filter",
            type=str,
            help="Filter to apply, default: filters ",
            required=False,
        ),
        click.option(
            "--order",
            type=click.Choice(["asc", "desc"]),
            help="Order to apply, default: desc",
            required=False,
        ),
        click.option(
            "--sort",
            type=click.Choice(["creation", "reputation", "name"]),
            help="Sort to apply, default: creation",
            required=False,
        ),
        click.option(
            "--display-columns",
            "-dc",
            multiple=True,
            default=["display_name", "user_id", "reputation", "last_access_date"],
            help="""Columns to display:
        usage: -dc display_name -dc user_id -dc reputation -dc last_access_date
        
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
        ),
    ]
    return wrap_options(func=func, options=options)
