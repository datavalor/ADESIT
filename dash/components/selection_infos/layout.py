import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table

from .cyto_utils import gen_cyto
from .help import help_infos
from utils.dash_utils import gen_help_tooltips

def render():
    return dbc.Collapse(
        [
            html.Hr(),
            html.H5([
                'Selection Infos', 
                html.I(
                    id="selection-help",
                    className="fas fa-question-circle",
                    style={
                        'display' : 'inline-block',
                        'margin' :'5px',
                    }
                ),
            ]),

            html.Div([
                dbc.Button('CLEAR SELECTION', 
                    color="primary", 
                    id='clear-selection-button', 
                    disabled=True,
                    style={'display':'inline-block', 'marginRight': '10px'}
                ),
                html.Span('Click on a point/line to analyse a tuple!', id="ceviz_selection_infos"),
            ], style= {'margin' : '0 auto', "marginTop": "5px"}),
            html.Div(
                [
                    dbc.Collapse(
                        html.Div(
                            [
                                html.Div(
                                    gen_cyto(),
                                    id="cyto_container",
                                    style={'width': '50%', 'height': '100%', "float": "left"}
                                ),
                                html.Div(
                                    [
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
                                        ], style={"display" : "table-row", "verticalAlign" : "bottom", "height" : "1px"})
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
                            style={
                                'width': '100%', 
                                'height': '350px', 
                                'marginTop': '10px', 
                                "marginBottom": '10px'
                            },
                        ),
                        id='selection-graph-collapse',
                        is_open=False
                    ),
                    dbc.Collapse(
                        html.Div(
                            [
                                dash_table.DataTable(
                                        id="selection-datatable",
                                        page_size=15
                                ),
                            ],
                            id="ceviz_table_container"
                        ),
                        style={
                            'marginTop': '10px',
                        },
                        id='selection-table-collapse',
                        is_open=False
                    ),
                ],
            ),
            *gen_help_tooltips(help_infos)
        ], 
        style={
            'marginLeft' : '0%', 
            'marginRight' : '0%',
            'height' : '750px'
        },
        id="collapse-ceviz",
        is_open=False
    )