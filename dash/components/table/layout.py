import dash_html_components as html

import dash_table

def render():
    return html.Div(
        [
            dash_table.DataTable(
                id="dataTable",
                page_size=15
            )
        ], 
        id="table-container"
    )