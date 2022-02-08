from dash import html
from dash import dash_table

from constants import *

def render():
    return [
            html.Div("", style={'width': "100%", 'height': "10px"}),
            html.Div(
                [
                    dash_table.DataTable(
                        id="viz_datatable",
                        page_size=TABLE_MAX_ROWS
                    )
                ], 
                id="viz_table_container"
            )
    ]