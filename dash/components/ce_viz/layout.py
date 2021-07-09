import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import dash_cytoscape as cyto
from dash_html_components.Hr import Hr
import dash_table

from constants import *

def render():
    return dbc.Collapse(
        [
            html.Hr(),
            html.H5("Selection infos"),
            html.Div([
                    cyto.Cytoscape(
                        id='cytoscape_ce_graph',
                        layout={
                            'name': 'breadthfirst'
                        },
                        stylesheet=[
                            {
                                'selector': 'node',
                                'style': {
                                    'content': 'data(label)',
                                    'border': '2px lightgrey black'
                                }
                            },
                            {
                                'selector': '.selected_node_bad',
                                'style': {'background-color': SELECTED_COLOR_BAD}
                            },
                            {
                                'selector': '.selected_node_good',
                                'style': {'background-color': SELECTED_COLOR_GOOD}
                            },
                            {
                                'selector': '.ce_node',
                                'style': {'background-color': CE_COLOR}
                            },
                            {
                                'selector': '.undirect_edges',
                                'style': {'line-color': 'lightgray'}
                            },
                            {
                                'selector': '.direct_edges',
                                'style': {'line-color': 'darkgray'}
                            }
                        ],
                        elements=[],
                        style={'width': '50%', 'height': '100%', "float": "left", 'backgroundColor': GRAPHS_BACKGROUND}
                    ),
                    html.Div(
                        [   
                            html.Div("No tuple seclected.", id="ceviz_selection_infos"),
                            html.Hr(),
                            html.Strong("Graph depth"),
                            html.Div(
                                dcc.Slider(
                                    id='graph_depth_slider',
                                    min=1,
                                    max=10,
                                    step=1,
                                    value=2,
                                    marks={n:str(n) for n in list(range(1, 11))}
                                )
                            )
                        ],
                        style={'width': '50%', "paddingLeft": "20px", "float": "right", "height": "100%"}
                    ),
                ],
                style={'width': "100%", 'height': "350px", "marginTop": "10px", "marginBottom": "10px"}
            ),
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