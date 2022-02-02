from dash import html
from dash import dash_table

import dash_bootstrap_components as dbc

def render():
    return [
        html.Div("", style={'width': "100%", 'height': "10px"}),
        html.Div(
            [
                dash_table.DataTable(
                    id="viz_datatable",
                    page_size=15
                )
            ], 
            id="viz_table_container"
        )
    ]