from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from typing import Any
from rich.style import Style
from rich.align import Align


def build_rich_table(table_title: str,
                     table_data: list[dict[str, Any]],
                     display_columns: tuple[str],
                     add_panel: bool, panel_data: dict[str, Any] | None = None
                     ) -> None:
    
    table = Table(title=table_title, expand=True)
    console = Console()

    if table_data:
        try:
            table.add_column("#", style="white", no_wrap=True, justify="center")
            for column in display_columns:
                table.add_column(
                    column, style="cyan", no_wrap=True, justify="center", min_width=5
                )


            dim1 = Style(color="steel_blue1")
            dim2 = Style(color="cyan2") 
            for i, data_entry in enumerate(table_data, start=1):
                style = dim1 if i % 2 == 0 else dim2
                table.add_row(
                    str(i),
                    *[
                        str(data_entry[column]) if column in data_entry else "N/A"
                        for column in display_columns
                    ], style=style
                )
        except Exception as e:
            print(e)

        console = Console()

        if add_panel and panel_data:
            style = Style(color="grey78")
            panel_data_str = " - ".join([f"{k} | {v}" for k, v in panel_data.items()])
            panel_data_panel = Panel(
                Align.center(panel_data_str), title="Meta", expand=True, style=style
            )
            group = Group(table, panel_data_panel)
            console.print(group)
        else:
            console.print(table)
    else:
        
        console.print("No data found", style="red")