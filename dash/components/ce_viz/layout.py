import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import dash_cytoscape as cyto
import dash_table

def render():
    return [
        html.Div("", style={'width': "100%", 'height': "10px"}),
        html.Div(
            [
                dash_table.DataTable(
                        id="ceviz_datatable",
                        page_size=15
                ),
            ],
            id="ceviz_table_container"
        ),
        # html.Div("", style={'width': "100%", 'height': "10px"}),
        # cyto.Cytoscape(
        #     id='cytoscape-elements-basic',
        #     layout={'name': 'preset'},
        #     style={'width': '50%', 'height': '400px', 'backgroundColor': '#F5F5F5'},
        #     elements=[
        #         # The nodes elements
        #         {'data': {'id': 'one', 'label': 'Node 1'},
        #         'position': {'x': 50, 'y': 50}},
        #         {'data': {'id': 'two', 'label': 'Node 2'},
        #         'position': {'x': 200, 'y': 200}},

        #         # The edge elements
        #         {'data': {'source': 'one', 'target': 'two', 'label': 'Node 1 to 2'}}
        #     ]
        # ),
    ]