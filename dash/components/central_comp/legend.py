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
        ]),
        style= {
           "width": "50%",
           "marginRight": "10px",
           "display": "inline-block"
        }
    )