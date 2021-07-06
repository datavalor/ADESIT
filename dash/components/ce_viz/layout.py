import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import dash_cytoscape as cyto
import dash_table

from constants import *

def render():
    return dbc.Collapse(
        [
            html.Hr(),
            html.H5("Selection infos"),
            html.Div("", style={'width': "100%", 'height': "10px"}),
            # cyto.Cytoscape(
            #     id='cytoscape_ce_graph',
            #     layout={'name': 'cose'},
            #     style={'width': '50%', 'height': '400px', 'backgroundColor': '#F5F5F5'},
            #     stylesheet=[
            #         {
            #             'selector': 'node',
            #             'style': {
            #                 'content': 'data(label)',
            #                 'border': 'thin lightgrey solid'
            #             }
            #         },
            #         {
            #             'selector': '.selected_node',
            #             'style': {'background-color': SELECTED_COLOR_BAD}
            #         },
            #         {
            #             'selector': '.ce_node',
            #             'style': {'background-color': CE_COLOR}
            #         },
            #         {
            #             'selector': '.undirect_edges',
            #             'style': {'line-style': 'dashed'}
            #         }
            #     ],
            #     elements=[]
            # ),
            # html.Div("", style={'width': "100%", 'height': "10px"}),
            html.Div(
                [
                    dash_table.DataTable(
                            id="ceviz_datatable",
                            page_size=15
                    ),
                ],
                id="ceviz_table_container"
            ),
        ], 
        style={
            'marginLeft' : '0%', 
            'marginRight' : '0%',
            'height' : '750px'
        },
        id="collapse-ceviz",
        is_open=False
    )