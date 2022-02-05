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
            html.Div("Y-Axis"),
            dcc.Dropdown(id='time_trace_yaxis',style={'width' : '100%', 'marginBottom' : '10px'}),

        ], style={
            'width': '29%',
            'display': 'inline-block',
            'verticalAlign': 'top'
        }),
    ]