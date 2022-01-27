import dash_bootstrap_components as dbc
from dash import html

from utils.dash_utils import Tooltip

from constants import *

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

def gen_analysed_legend():
    return dbc.Card(
        dbc.CardBody([
            Tooltip(children=["Tuple involved in no counterexample."], target='free_tuple_tooltip'),
            Tooltip(children=["Tuple involved in at least 1 counterexample."], target='involved_tuple_tooltip'),
            html.Strong(
                [
                    html.Span(
                        "Free tuple",
                        id="free_tuple_tooltip",
                        style={
                            'textDecoration': 'underline', 
                            'cursor': 'pointer'
                        }
                    ),
                    ": "
                ], 
                style={
                    "marginRight": "10px", 
                    "verticalAlign": "top"
                }
            ),
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
            html.Strong(
                [
                    html.Span(
                        "Involved tuple",
                        id="involved_tuple_tooltip",
                        style={
                            'textDecoration': 'underline', 
                            'cursor': 'pointer'
                        }
                    ),
                    ": "
                ], 
                style={
                    "marginRight": "10px", 
                    "verticalAlign": "top"
                }
            ),
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
        ]),
        style= {
           "width": "50%",
           "marginRight": "10px",
           "display": "inline-block"
        }
    )

def gen_time_controller():
    return dbc.Card(
        dbc.CardBody([
            html.Strong("Time attribute:", style={
                "marginRight": "10px", 
                "verticalAlign": "top",
            }),
            dbc.Select(id='time-attribute-dropdown', 
                options=[
                    {'label': 'No attribute selected', 'value': 'noattradesit'}
                ],
                value='noattr',
                disabled=False,
                style={
                    'display': 'inline-block', 
                    'width': '200px',
                    'marginRight': '20px'
                }
            ),
            html.Strong("Group by:", style={
                "marginRight": "10px", 
                "verticalAlign": "top",
            }),
            dbc.Select(id='time-period-dropdown', 
                options=[
                    {'label': 'Don\'t group', 'value': 'nogroup'},
                ],
                value='nogroup',
                disabled=False,
                style={
                    'display': 'inline-block', 
                    'width': '150px'
                }
            ),
            html.Br(),
            html.Strong("Attribute period: "), html.Strong("N/A", id="time-range"),
            html.Br(),
            html.Strong("Current period: "), html.Strong("N/A", id="current-time-range"),
            html.Br(),
            dbc.Button(
                "←", id="time-backward-button", className="me-2", n_clicks=0,
                disabled=True
            ),
            html.Span("1", id="current-time-range-number"), 
            html.Span("/"),
            html.Span("1", id="max-time-range-number"),
            dbc.Button(
                "→", id="time-forward-button", className="me-2", n_clicks=0,
                disabled=True,
                style={"marginLeft":"10px"}
            ),
        ]),
        style= {
           "width": "45%",
           "marginLeft": "10px",
           "display": "inline-block",
        }
    )