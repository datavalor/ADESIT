import dash_html_components as html

import dash_table

def render():
    return [
        html.Div("", style={'width': "100%", 'height': "10px"}),
        html.Div(
            [
                
                dash_table.DataTable(
                    id="dataTable",
                    page_size=15
                )
            ], 
            id="table-container"
        )
    ]