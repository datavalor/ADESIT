import dash_bootstrap_components as dbc
import dash_html_components as html

import dash_core_components as dcc
from components import table as table_component
from components import scatter_view as scatter_view_component

from constants import *

def render():
    def gen_legend_element(color, title):
        return html.Div(
            [
                html.Div([], style={
                    "height": "20px",
                    "width": "20px",
                    "backgroundColor": color,
                    'display': 'inline-block',
                    "marginRight": "10px"
                }),
                html.Span(title, style={"verticalAlign": "top"})
            ]
            , style={'display': 'inline-block', 'marginRight': '10px'}
        )

    return dbc.Collapse(
        [
            html.H5("Dataset exploration"),
            dbc.Collapse(dbc.Card(dbc.CardBody([
                html.Strong("Free tuple: ", style={
                    "marginRight": "10px", 
                    "verticalAlign": "top",
                }),
                gen_legend_element(FREE_COLOR, "Unselected"),
                gen_legend_element(SELECTED_COLOR_GOOD, "Selected"),
                html.Div([], style=
                    {
                        "width": "0px",
                        'display': 'inline-block',
                        'borderRight': "1px solid",
                        "height": "20px",
                        "marginRight": "6px",
                        "marginLeft": "5px",
                    }
                ),
                html.Strong("Involved tuple:", style={
                    "marginRight": "10px", 
                    "verticalAlign": "top",
                }),
                gen_legend_element(CE_COLOR, "Unselected"),
                gen_legend_element(SELECTED_COLOR_BAD, "Selected"),
                html.Br(),
                html.Strong("Filter by color:", style={
                    "marginRight": "10px", 
                    "verticalAlign": "top",
                }),
                dbc.Select(id='view', 
                    options=[
                        {'label': 'All', 'value': 'ALL'},
                        {'label': 'Blue Only', 'value': 'NP'},
                        {'label': 'Red Only', 'value': 'P'},
                    ],
                    value='ALL',
                    disabled=True,
                    style={
                        'display': 'inline-block',
                        'width': '120px',
                        'marginRight': '20px'
                    }
                ),
                html.Strong("Color in red:", style={
                    "marginRight": "10px", 
                    "verticalAlign": "top",
                }),
                dbc.Select(id='mode', 
                    options=[
                        {'label': 'Tuples involved in a counterexample', 'value': 'color_involved'},
                        {'label': 'Tuples to suppress to remove all counterexamples', 'value': 'color_g3'}
                    ],
                    value='color_involved',
                    disabled=True,
                    style={
                        'display': 'inline-block', 
                        'width': '375px'
                    }
                ),
                html.Div([
                    html.Span("Click on a point/line to analyse a specific tuple!"),
                    dbc.Button('CLEAR SELECTION', 
                        color="primary", 
                        id='clear-selection', 
                        disabled=True,
                        style={'display':'inline-block', 'marginLeft': '10px'}
                    ),
                ], style= {'margin' : '0 auto', "marginTop": "5px"}),
            ])),
                id="collapse-legend",
                is_open=False,
                style={
                    "width": "60%",
                    'margin': '0 auto',
                    'padding': '20px',
                    'textAlign': 'center'
                }
            ),
            dbc.Tabs([
                dbc.Tab(table_component.render(), label="Table"),
                dbc.Tab(scatter_view_component.render(), label="2D Scatter View"),
            ])
        ], 
        style={
            'marginLeft' : '0%', 
            'marginRight' : '0%',
            'height': '865px'
        },
        id="collapse-viz",
        is_open=False
    )