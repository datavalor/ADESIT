import dash_bootstrap_components as dbc
from dash import html

from utils.dash_utils import Tooltip

from constants import *

def gen_legend_element(color, title):
    return html.Div(
        [
            html.Div([], style={
                'height': '20px',
                'width': '20px',
                'backgroundColor': color,
                'display': 'inline-block',
                'marginRight': '10px',
                'verticalAlign': 'middle'
            }),
            html.Span(title, style={'verticalAlign': 'middle'})
        ]
        , style={'display': 'inline-block', 'marginRight': '10px'}
    )

def gen_legend_seprator():
    return html.Div(
        [], 
        style={
            'width': '0px',
            'display': 'inline-block',
            'borderRight': '1px solid',
            'height': '20px',
            'marginRight': '6px',
            'marginLeft': '5px',
            'verticalAlign': 'middle'
        }
    )

def gen_analysed_legend():
    return dbc.Card(
        dbc.CardBody([
            html.I(
                id="free-tuple-help",
                className="fas fa-question-circle",
                style={
                    'display' : 'inline-block',
                    'margin' : '5px'
                }
            ),
            html.Strong(
                'Free tuple:', 
                style={
                    'marginRight': '10px', 
                    'verticalAlign': 'middle'
                }
            ),
            gen_legend_element(FREE_COLOR, "Unselected"),
            gen_legend_element(SELECTED_COLOR_GOOD, "Selected"),
            gen_legend_seprator(),
            html.I(
                id="involved-tuple-help",
                className="fas fa-question-circle",
                style={
                    'display' : 'inline-block',
                    'margin' : '5px'}
            ),
            html.Strong(
                'Involved tuple:', 
                style={
                    'marginRight': '10px', 
                    'verticalAlign': 'middle'
                }
            ),
            gen_legend_element(CE_COLOR, 'Unselected'),
            gen_legend_element(SELECTED_COLOR_BAD, 'Selected'),
            gen_legend_seprator(),
            html.Strong(
                'Filter by color:', 
                style={
                    'marginRight': '10px', 
                    'marginLeft': '5px',
                    'verticalAlign': 'middle',
                }
            ),
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
            html.Span(
                [
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
                ], 
                style={'display': 'none'}
            )
        ]),
        style= {
           "width": "70%",
           "marginRight": "10px",
           "display": "inline-block"
        }
    )