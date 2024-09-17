import click
from typing import Any, Callable
from cli.utility import wrap_options


def view_options(func: Callable) -> Callable[..., Any]:
    options = [
        click.option(
            "--page-size",
            "-ps",
            type=int,
            default=10,
            help="number of users to display per page",
            required=False,
        ),
        click.option(
            "--page",
            "-p",
            type=int,
            default=1,
            help="page number to display",
            required=False,
        ),
        click.option(
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
        ),
        click.option(
            "--user-ids",
            "-id",
            multiple=True,
            type=int,
            help="specify the user ids",
            required=False,
        ),
    ]

    return wrap_options(func, options=options)


def add_options(func: Callable) -> Callable[..., Any]:
    options = [
        click.option(
            "--user-id",
            "-id",
            multiple=True,
            type=int,
            help="specify the user ids",
            required=False,
        ),
    ]
    return wrap_options(func, options=options)


def remove_options(func: Callable) -> Callable[..., Any]:
    options = [
        click.option(
            "--user-ids",
            "-id",
            multiple=True,
            type=int,
            help="specify the user ids",
            required=False,
        ),
        click.option(
            "--all",
            "-a",
            is_flag=True,
            default=False,
            help="Display all columns",
            required=False,
        ),
    ]

    return wrap_options(func=func, options=options)
