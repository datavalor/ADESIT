import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import dash_table

from .cyto_utils import gen_cyto

def render():
    return dbc.Collapse(
        [
            html.Hr(),
            html.H5("Selection infos"),
            html.Div(
                [
                    html.Div(
                        gen_cyto(),
                        id="cyto_container",
                        style={'width': '50%', 'height': '100%', "float": "left"}
                    ),
                    html.Div(
                        [   
                            html.Div("No tuple seclected.", id="ceviz_selection_infos"),
                            html.Strong("Hovered node content:"),
                            html.Div(id="ceviz_hovered_node"),
                            html.Div([
                                html.Hr(),
                                html.Strong("Graph depth"),
                                html.Div(
                                    dcc.Slider(
                                        id='graph_depth_slider',
                                        min=1,
                                        max=5,
                                        step=1,
                                        value=2,
                                        marks={n:str(n) for n in list(range(1, 6))}
                                    )
                                )
                            ], style={"display" : "table-row", "vertical-align" : "bottom", "height" : "1px"})
                        ],
                        style= {
                                'width': '50%', 
                                "paddingLeft": "20px", 
                                "float": "right", 
                                "height": "100%",
                                "display": "table"
                            }
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