import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

from utils.dash_utils import gen_modal

def render():
    return [
        html.Div("", style={'width': "100%", 'height': "10px"}),

        # Graph
        html.Div([
                dcc.Graph(
                    id='time_trace_graph', 
                    clear_on_unhover=True
                )
            ], 
            style={
                'textAlign' : 'center',
                'width': '69%',
                'display': 'inline-block',
                'marginBottom' : '25px',
            }
        ),
        
        # Commands Board
        html.Div([
            dbc.Label('Y-Axis'),
            dbc.Select(
                id='timetrace-yaxis-dropdown', 
                style={'width' : '100%', 'marginBottom' : '10px'},
            ),
            dbc.Label('Display options'),
            dbc.Checklist(
                options=[
                    {"label": "Show time cuts", "value": 0},
                    {"label": "Follow time period", "value": 1},
                ],
                value=[],
                id="time-trace-viz-switches",
                switch=True,
            ),
            dbc.Button(
                'Center on current time period', id="time-trace-center-button", className="me-2", n_clicks=0,
                style={
                    'width': '100%'
                }
            )

        ], style={
            'width': '29%',
            'display': 'inline-block',
            'verticalAlign': 'top'
        }),
    ]