from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from typing import Any
from rich.style import Style
from rich.align import Align
from rich.progress import Progress, TimeRemainingColumn, BarColumn
import time

console = Console()


def build_rich_table(table_title: str, display_columns: tuple) -> Table:

    table = Table(title=table_title, expand=True)
    try:
        table.add_column("#", style="white", no_wrap=True, justify="center")
        for column in display_columns:
            table.add_column(
                column, style="cyan", no_wrap=True, justify="center", min_width=5
            )
        return table
    except Exception as e:
        raise e


def build_rich_view(items: list[Any]) -> None:
    console.clear()
    group = Group(*items)
    console.print(group)


def add_rich_panel(panel_data: dict[str, Any], title: str) -> Panel:
    if panel_data:
        style = Style(color="grey78")
        panel_data_str = " - ".join([f"{k} | {v}" for k, v in panel_data.items()])
        panel_data_panel = Panel(
            Align.center(panel_data_str), title=title, expand=True, style=style
        )
        return panel_data_panel
    else:
        raise ValueError("No panel data found")


def add_rich_row(
    table: Table, table_data: list[dict[str, Any]], display_columns: list[str]
) -> None:

    if not table_data:
        raise ValueError("No data to add to table")

    dim1 = Style(color="steel_blue1")
    dim2 = Style(color="cyan2")
    for i, data_entry in enumerate(table_data, start=1):
        style = dim1 if i % 2 == 0 else dim2

        row = []
        for column in display_columns:
            if column in data_entry:
                row.append(str(data_entry[column]))
            else:
                row.append("N/A")

        table.add_row(
            str(i),
            *row,
            style=style,
        )


def build_rich_timer_bar(total_time: int, desc: str) -> None:
    console.clear()
    progress = Progress(
        "{task.description}",
        BarColumn(),
        TimeRemainingColumn(),
    )
    task = progress.add_task(f"[cyan]{desc}", total=total_time)
    with Live(
        Align.center(Panel(progress, padding=(2, 10))),
        console=console,
        refresh_per_second=2,
    ):
        for tick in range(total_time):
            time.sleep(1)
            progress.advance(task)
